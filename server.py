from model import User, Board, BoardImage, Image, ImageTag, BoardTag, Tag, connect_to_db, db
import requests
import os
from urllib import urlencode, quote_plus
import json
from flask import Flask, request, render_template, session, jsonify
# redirect was getting overwritten somehow - solution for now
from flask import redirect as flaskredirect


CLIENT_ID = os.environ['PINTEREST_CLIENT_ID']
APP_SECRET = os.environ['PINTEREST_APP_SECRET']

# My Global access_token. Need to use session to store user's access token
ACCESS_TOKEN1 = os.environ['ACCESS_TOKEN']

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"


# 1
@app.route('/')
def welcome():
    """Website Welcome Page"""

    # if session['user_id']:
    #     return flaskredirect('/home')
    # else:
    #     return render_template('homepage.html')

    try:
        if session['user_id']:
            return flaskredirect('/home')
        else:
            return render_template('homepage.html')
    except KeyError:
        return render_template('homepage.html')



# OAuth and Log In Start ------------------------------------------------------------
# 2
@app.route('/login')
def login():
    """OAuth - Redirect user to log in"""

    # Data that pinterest requests is sent
    auth_data = {
                # Pinterest says to use 'code'
                'response_type': 'code',
                # Route I want Pinterest to go to once user logs in and Pinterest processes the log in
                # Need to remember to register this redirect route on pinterest app!
                'redirect_uri': 'https://localhost:5000/process_login',
                # My apps's client_id, so pinterest know's who's redirecting the user to their page
                'client_id': CLIENT_ID,
                # What I want to be able to do with user's account
                'scope': 'read_public,write_public,read_relationships,write_relationships',
                # Note for myself
                'state': 'Random!'
    }

    url = 'https://api.pinterest.com/oauth?'

    # urlencode changes auth_data into url string, redirect needs url, can't take params
    # need to import urlencode from urllib
    full_url = url + urlencode(auth_data)

    return flaskredirect(full_url)


# 3
@app.route('/process_login')
def redirect():
    """render new html template!"""

    # Data I need to send to Pinterest to retrieve access_token
    request_data = {
        'grant_type': 'authorization_code',
        # My app's client_id and client_secret, so Pinterest knows who is requesting the user's access token
        'client_id': CLIENT_ID,
        'client_secret': APP_SECRET,
        # Grabbing code from pinterest that is sent when pinterest redirect's to this route
        'code': request.args.get('code')
    }

    # Add data to url for post to Pinterest to ask for access token
    response = requests.post('https://api.pinterest.com/v1/oauth/token', data=request_data)
    auth_response = response.json()
    access_token = auth_response['access_token']

    headers = {'Authorization': 'Bearer %s' % access_token}
    payload = {'fields': 'id,username,first_name,last_name,bio'}
    user_info_request = requests.get('https://api.pinterest.com/v1/me', headers=headers, params=payload)
    user_info = user_info_request.json()

    # Query to check if user exists in the db
    user_exists = User.query.filter(User.pinterest_user_id == user_info['data']['id']).first()

    if user_exists:
        session['user_id'] = user_exists.user_id
        session['username'] = user_exists.username
        # Eventually remove access token from sesison and grab it through db query
        session['access_token'] = user_exists.access_token
        print "User Exists"
    else:
        print "New User"
        pinterest_user_id = user_info['data']['id']
        username = user_info['data']['username']
        first_name = user_info['data']['first_name']
        last_name = user_info['data']['last_name']
        bio = user_info['data']['bio']

        # Create new_user for db
        new_user = User(pinterest_user_id=pinterest_user_id, username=username, first_name=first_name,
                        last_name=last_name, bio=bio, access_token=access_token)

        db.session.add(new_user)
        db.session.commit()

        # Add user_id and access_token to session for global use
        session['user_id'] = new_user.user_id
        session['username'] = new_user.username
        # Eventually remove access token from sesison and grab it through db query
        session['access_token'] = new_user.access_token

        print

    return flaskredirect('/home')

# OAuth and Log In End ---------------------------------------------------------------


# 4
@app.route('/logout')
def logout():
    session.clear()
    print "LOGGED OUT"

    return render_template('homepage.html')


# 5
@app.route('/home')
def home():
    """Lists user's boards that are saved to blines db"""
    user_boards = Board.query.filter(Board.user_id == session['user_id']).all()

    print user_boards
    return render_template('home.html',
                            user_boards=user_boards,
                            username=session['username'])


# 6
@app.route('/user_board_images/<int:board_id>')
def images_in_blines(board_id):
    """Displays images from chosen board that exist in blines db"""

    images = Board.query.get(board_id).images
    boards_in_blines = Board.query.filter(Board.user_id == session['user_id']).all()
    current_board = Board.query.filter(Board.board_id == board_id).first()

    return render_template('pinterest_board.html',
                            images=images,
                            boards=boards_in_blines,
                            current_board=current_board)


# 7
@app.route('/pinterest_boards')
def pinterest_boards():
    """Displays all of user's boards from their pinterest"""

    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/', headers=headers, params=payload)
    boards_request = new_request.json()
    # FIX ME - do I still need enumerate?
    for index, board in enumerate(boards_request['data']):
        url = board['url']
        url = url.split('/')
        board_name = url[-2]
        board['url'] = board_name

    return render_template('user_pinterest.html',
                            boards=boards_request,
                            username=session['username'])


# 8
@app.route('/pinterest_board_images/<url>')
def show_pinterest_boards(url):
    """Displays pins from user chosen board that is on pinterest"""

    # import pdb; pdb.set_trace()

    user = User.query.filter(User.user_id == session['user_id']).first()
    username = user.username
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note', 'limit': 100}
    # apiRequest = ApiRequest(access_token)
    # apiRequest.getPins(username, url, params)
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s/pins' % (username, url), headers=headers, params=payload)
    pins_request = new_request.json()

    # Make multiple requests to pinterest since the pin request limit is 100
    next_request = pins_request['page']['next']
    all_pins = pins_request['data']

    while next_request is not None:
        new_request = requests.get(next_request, headers=headers, params=payload)
        pins_request = new_request.json()
        all_pins.extend(pins_request['data'])
        next_request = pins_request['page']['next']

    # Sending boards in blines db to display in modal if user wants to save image
    boards_in_blines = Board.query.filter(Board.user_id == session['user_id']).all()

    return render_template('pinterest_board.html',
                            pins=all_pins,
                            boards=boards_in_blines)


# 9
@app.route('/save_board', methods=['POST'])
def save_board():
    """Saves board to Beautiful Lines"""

    board = request.form.get('board_url')

    username = session['username']
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s' % (username, board), headers=headers, params=payload)
    board_request = new_request.json()

    pinterest_board_id = board_request['data']['id']
    board_name = board_request['data']['name']
    board_description = board_request['data']['description']
    image_url = board_request['data']['image']['60x60']['url']

    # Create new_board for db
    new_board = Board(pinterest_board_id=pinterest_board_id,
                      url_name=board,
                      board_name=board_name,
                      board_description=board_description.lower(),
                      image_url=image_url,
                      user_id=session['user_id'])

    db.session.add(new_board)
    db.session.commit()

    new_tag = Tag(tag_content=new_board.board_description.lower(),
                  user_id=session['user_id'])
    new_tag2 = Tag(tag_content=new_board.board_name.lower(),
                   user_id=session['user_id'])

    db.session.add(new_tag)
    db.session.add(new_tag2)
    db.session.commit()

    new_boardtag = BoardTag(board_id=new_board.board_id,
                            tag_id=new_tag.tag_id)

    new_boardtag2 = BoardTag(board_id=new_board.board_id,
                             tag_id=new_tag2.tag_id)

    db.session.add(new_boardtag)
    db.session.add(new_boardtag2)
    db.session.commit()

    session['board_id'] = new_board.board_id
    session['board_url'] = new_board.url_name

    # After saving the board, need to save the images that are on the board
    return flaskredirect('/save_images_on_board')


# 10
@app.route('/save_images_on_board')
def save_images_on_board():

    user = User.query.filter(User.user_id == session['user_id']).first()
    username = user.username
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s/pins' % (username, session['board_url']), headers=headers, params=payload)
    pins_request = new_request.json()

    # Make multiple requests to pinterest since the pin request limit is 100
    next_request = pins_request['page']['next']
    all_pins = pins_request['data']

    while next_request is not None:
        new_request = requests.get(next_request, headers=headers, params=payload)
        pins_request = new_request.json()
        all_pins.extend(pins_request['data'])
        next_request = pins_request['page']['next']

    board = Board.query.filter(Board.board_id == session['board_id']).first()

    # Save each image in pins_request['data'] to images table


    for pin in all_pins:
        # Check if image exists in db
        check_image = Image.query.filter(Image.pinterest_image_id == pin['id']).first()
        print check_image
        print '**************************************************'

        if check_image is None:
            pinterest_image_id = pin['id']
            original_url = pin['image']['original']['url']
            pinterest_url = pin['url']
            description = pin['note']

            # Create new_image for db
            new_image = Image(pinterest_image_id=pinterest_image_id,
                              original_url=original_url,
                              pinterest_url=pinterest_url,
                              description=description)

            db.session.add(new_image)
            db.session.commit()

            new_tag = Tag(tag_content=new_image.description.lower(),
                          user_id=user.user_id)

            db.session.add(new_tag)
            db.session.commit()

            new_imagetag = ImageTag(image_id=new_image.image_id,
                                    tag_id=new_tag.tag_id)

            db.session.add(new_imagetag)
            db.session.commit()

        else:
            new_image = check_image

        # Create new record for boards_images association table to save each image_id with board_id
        new_boardimage = BoardImage(board_id=board.board_id,
                                    image_id=new_image.image_id)

        db.session.add(new_boardimage)
        db.session.commit()

    return ('Board Saved')

#11
@app.route('/edit_board', methods=['POST'])
def edit_board():
    """Edits user board"""

    new_title = request.form.get('new_board_title')
    new_description = request.form.get('new_board_description')
    board_id = request.form.get('board_id')

    board = Board.query.get(board_id)

    tags = board.tags
    print '**********************************************************************'
    print 'Tags: %s' % tags

    for tag in tags:
        if tag.tag_content == board.board_name.lower():
            tag.tag_content = new_title.lower()
        if tag.tag_content == board.board_description.lower():
            tag.tag_content = new_description.lower()

    board.board_name = new_title
    board.board_description = new_description

    db.session.commit()

    return ('Board Edited')


# 12
@app.route('/delete_board', methods=['POST'])
def delete_board():
    """Deletes user board from blines db and associated images and tags that don't exist in other boards"""

    board_id = request.form.get('board_id')

    images_ids = []
    ok_to_delete_images = []
    tags = []

    images = Board.query.get(board_id).images
    for image in images:
        images_ids.append(image.image_id)

    # Delete from board association tables(foreign keys)
    BoardImage.query.filter(BoardImage.board_id == board_id).delete()
    boardtags = BoardTag.query.filter(BoardTag.board_id == board_id).all()
    for boardtag in boardtags:
        tags.append(Tag.query.filter(Tag.tag_id == boardtag.tag_id).first())
    BoardTag.query.filter(BoardTag.board_id == board_id).delete()

    db.session.commit()

    # Find out which images are still needed in db for other boards
    for next_image_id in images_ids:
        check_board_image = BoardImage.query.filter(BoardImage.image_id == next_image_id).first()

        if check_board_image is None:
            ok_to_delete_images.append(Image.query.filter(Image.image_id == next_image_id).first())
            image_tag = ImageTag.query.filter(ImageTag.image_id == next_image_id).first()
            tags.append(Tag.query.filter(Tag.tag_id == image_tag.tag_id).first())
            ImageTag.query.filter(ImageTag.image_id == next_image_id).delete()

    for image in ok_to_delete_images:
        Image.query.filter(Image.image_id == image.image_id).delete()

    # Delete tags now that they are no longer associated with images
    for tag in tags:
        Tag.query.filter(Tag.tag_id == tag.tag_id).delete()

    # Finally, delete actual board
    Board.query.filter(Board.board_id == board_id).delete()

    db.session.commit()

    return ('Board Deleted')


# FIX ME - Can't save a specific image to a board more than once
# (shows ups more than once in boards_images table, but doesn't appear on page twice) why??
# 13
@app.route('/save_image', methods=['POST'])
def save_image():
    """Saves image to Beautiful Lines Board"""

    board_id = request.form.get('board')
    pin_id = request.form.get('pin_id')
    image_id = request.form.get('image_id')

    # If image not already in db
    if image_id == "No-ID":

        headers = {'Authorization': 'Bearer %s' % session['access_token']}
        payload = {'fields': 'id,url,board,image,note'}
        new_request = requests.get('https://api.pinterest.com/v1/pins/%s' % (pin_id), headers=headers, params=payload)
        pin_request = new_request.json()

        # pinterest_image_id = pin_request['data']['id']
        original_url = pin_request['data']['image']['original']['url']
        pinterest_url = pin_request['data']['url']
        description = pin_request['data']['note']

        new_image = Image(pinterest_image_id=pin_id,
                          original_url=original_url,
                          pinterest_url=pinterest_url,
                          description=description)

        db.session.add(new_image)
        db.session.commit()

        new_tag = Tag(tag_content=new_image.description.lower(),
                      user_id=session['user_id'])

        db.session.add(new_tag)
        db.session.commit()

        new_imagetag = ImageTag(image_id=new_image.image_id,
                                tag_id=new_tag.tag_id)

        db.session.add(new_imagetag)
        db.session.commit()

        image_id = new_image.image_id

    new_boardimage = BoardImage(board_id=board_id,
                                image_id=image_id)

    # check if user id on tag is current user, otherwise add tag for image with current user id
    image = Image.query.filter(Image.image_id == image_id).first()
    tag = image.tags[0]

    if tag.user_id != session['user_id']:
        new_tag = Tag(tag_content=image.description.lower(),
                      user_id=session['user_id'])

        db.session.add(new_tag)
        db.session.commit()

        new_imagetag = ImageTag(image_id=image.image_id,
                                tag_id=new_tag.tag_id)

        db.session.add(new_imagetag)
        db.session.commit()

    db.session.add(new_boardimage)
    db.session.commit()

    print "******************************************"
    print 'USER ID'
    print session['user_id']
    print "New Tag: %s" % new_tag
    print "******************************************"

    return ('Saved')


# 14
@app.route('/edit_image', methods=['POST'])
def edit_image():
    """Edit user image"""

    new_description = request.form.get('new_image_description')
    image_id = request.form.get('image_id')

    image = Image.query.get(image_id)
    tags = image.tags
    tag = tags[0]

    image.description = new_description
    tag.tag_content = new_description.lower()
    db.session.commit()

    return ('Image Edited')


# 15
@app.route('/delete_image', methods=['POST'])
def delete_image():
    """Deletes user image from blines association table, and from images table if no instances of it exist in association table"""

    board_id = request.form.get('board_id')
    image_id = request.form.get('image_id')

    BoardImage.query.filter(BoardImage.image_id == image_id, BoardImage.board_id == board_id).delete()
    db.session.commit()

    # Check if image exists on any boards, if there are no more instances of that image in the association table,
    # Then image and associated tags should be deleted from db
    image_in_boards_images = BoardImage.query.filter(BoardImage.image_id == image_id).all()

    if not image_in_boards_images:
        image_tag = ImageTag.query.filter(ImageTag.image_id == image_id).first()
        tag = Tag.query.get(image_tag.tag_id)
        ImageTag.query.filter(ImageTag.image_id == image_id).delete()
        db.session.commit()

        Tag.query.filter(Tag.tag_id == tag.tag_id).delete()
        Image.query.filter(Image.image_id == image_id).delete()
        db.session.commit()

    return ('Image Deleted')


# 16
@app.route('/create_board')
def create_board():
    """Creates new board in blines db"""

    board_name = request.args.get('board_name')
    board_description = request.args.get('board_description')
    image_url = request.args.get('image_url')
    url_name = quote_plus('board_name')

    # Create new_board for db
    new_board = Board(url_name=url_name,
                      board_name=board_name,
                      board_description=board_description,
                      image_url=image_url,
                      user_id=session['user_id'])

    db.session.add(new_board)
    db.session.commit()

    return flaskredirect('/home')


# 17
@app.route('/create_image/<int:board_id>')
def create_image(board_id):
    """Creates new image in blines db"""

    image_url = request.args.get('image_url')
    description = request.args.get('image_description')

    # Create new_image for db
    new_image = Image(original_url=image_url,
                      description=description)

    db.session.add(new_image)
    db.session.commit()

    new_boardimage = BoardImage(board_id=board_id,
                                image_id=new_image.image_id)


    db.session.add(new_boardimage)
    db.session.commit()

    return flaskredirect('/user_board_images/%s' % board_id)


# 18
@app.route('/study_board/<int:board_id>')
def study_board(board_id):
    """Displays pins from board chosen by user to study"""

    images = Board.query.get(board_id).images
    current_board = Board.query.filter(Board.board_id == board_id).first()

    return render_template('study.html',
                            images=images,
                            current_board=current_board)


# 19
@app.route('/study_images', methods=['POST'])
def study():
    """Sends json of images to js for Study Session"""

    board_id = request.form.get('board_id')

    images = Board.query.get(board_id).images

    list_of_image_urls = []
    for image in images:
        list_of_image_urls.append(image.original_url)

    return json.dumps(list_of_image_urls)

# 20
@app.route('/search_bl')
def show_bl_search():
    """Search user's images and display images related to user search terms"""

    images = []
    image_urls = set()
    unique_images = []
    user_search = request.args.get('images-search')

    print user_search
    print '**********************************************'

    search_words = user_search.split()

    for search_word in search_words:
        tag_search = Tag.query.filter(Tag.tag_content.like('%' + search_word + '%')).all()

        for tag in tag_search:
            images.extend(tag.images)
            boards = tag.boards

            if boards:
                for board in boards:
                    images.extend(board.images)

    for image in images:
        image_urls.add(image.original_url)

    for image_url in image_urls:
        unique_images.append(Image.query.filter(Image.original_url == image_url).first())

    boards_in_blines = Board.query.filter(Board.user_id == session['user_id']).all()

    return render_template('pinterest_board.html',
                           images=unique_images,
                           boards=boards_in_blines)


@app.route('/search_user')
def show_user_search():
    """Search user's images and display images related to user search terms"""

    images = []
    image_urls = set()
    unique_images = []
    user_search = request.args.get('images-search')

    print user_search
    print session['user_id']
    print '**********************************************'

    search_words = user_search.split()

    for search_word in search_words:
        tag_search = Tag.query.filter(Tag.tag_content.like('%' + search_word + '%'), Tag.user_id == session['user_id']).all()

        print tag_search
        print '**********************************************'

        for tag in tag_search:
            images.extend(tag.images)
            boards = tag.boards

            if boards:
                for board in boards:
                    images.extend(board.images)

    for image in images:
        image_urls.add(image.original_url)

    for image_url in image_urls:
        unique_images.append(Image.query.filter(Image.original_url == image_url).first())

    boards_in_blines = Board.query.filter(Board.user_id == session['user_id']).all()

    return render_template('pinterest_board.html',
                           images=unique_images,
                           boards=boards_in_blines)




# End Routes ---------------------------------------------------------------------------

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    context = ('server-files/yourserver.crt', 'server-files/yourserver.key')
    app.run(ssl_context=context)
