from model import User, Board, BoardImage, Image, ImageTag, BoardTag, Tag, connect_to_db, db
import route_functions
import requests
import os
from urllib import urlencode, quote_plus
import json
from flask import Flask, request, render_template, session, flash
# redirect was being overwritten
from flask import redirect as flaskredirect


APP_ID = os.environ['PINTEREST_CLIENT_ID']
APP_SECRET = os.environ['PINTEREST_APP_SECRET']


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "abcdef")


# 1
@app.route('/')
def welcome():
    """Website Welcome Page"""

    try:
        if session['user_id']:
            return flaskredirect('/boards')
        else:
            return render_template('welcome_page.html')
    except KeyError:
        return render_template('welcome_page.html')


# OAuth and Log In Start ------------------------------------------------------------
# 2
@app.route('/login')
def login():
    """OAuth - Redirect user to log in"""

    # Data that pinterest requests is sent
    auth_data = {  # Pinterest says to use 'code'
                   'response_type': 'code',
                   # Route I want Pinterest to go to once user logs in and Pinterest processes the log in
                   # Need to remember to register this redirect route on pinterest app!
                   # 'redirect_uri': 'https://localhost:5000/process_login',
                   'redirect_uri': 'https://beautifulines.herokuapp.com/process_login',
                   # My apps's id, so pinterest know's who's redirecting the user to their page
                   'client_id': APP_ID,
                   # What I want to be able to do with user's account
                   'scope': 'read_public',
                   # 'scope': 'read_public',
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
        # My app's id and client_secret, so Pinterest knows who is requesting the user's access token
        'client_id': APP_ID,
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
        session['first_name'] = user_exists.first_name
        session['access_token'] = user_exists.access_token
    else:
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
        session['first_name'] = new_user.first_name
        session['access_token'] = new_user.access_token

    return flaskredirect('/boards')

# OAuth and Log In End ---------------------------------------------------------------


# 4
@app.route('/logout')
def logout():
    session.clear()

    return render_template('welcome_page.html')

#5
@app.route('/homepage')
def homepage():
    """Displays user's homepage - summary of user's boards, sessions, and projects"""

    return render_template('homepage.html')


# 6
@app.route('/boards')
def boards():
    """Lists user's boards that are saved to blines db"""

    if session['user_id']:
        user_boards = Board.query.filter(Board.user_id == session['user_id']).all()
        return render_template('boards.html',
                               user_boards=user_boards,
                               first_name=session['first_name'])
    else:
        return redirect('/')

#7     
@app.route('/projects')
def projects():
    """Displays user's projects"""

    return ('This page will display user projects')
    # return render_template('projects.html')

#8
@app.route('/resources')
def resources():
    """Displays user's resources"""

    return ('This page will display user resources')
    # return render_template('resources.html')

#9
# @app.route('/sessions')
# def sessions():
#     """Displays user's drawing sessions"""

#     return ('This page will display user past drawing sessions')
#     # return render_template('sessions.html')

#9
@app.route('/account')
def account():
    """Displays user's account"""

    return ('This page will display user account')
    # return render_template('sessions.html')

# 10
@app.route('/user_board_images/<int:board_id>')
def images_in_blines(board_id):
    """Displays images from chosen board that exist in blines db"""

    images = Board.query.get(board_id).images
    boards_in_blines = Board.query.filter(Board.user_id == session['user_id']).all()
    current_board = Board.query.filter(Board.board_id == board_id).first()

    empty_board = False
    if not images:
        empty_board = True

    return render_template('pinterest_board.html',
                           images=images,
                           boards=boards_in_blines,
                           current_board=current_board,
                           empty_board=empty_board)


# FIX ME - What if user has more boards than initial request???
# Need to loop through request just like in /pinterest_board_images
# 11
@app.route('/pinterest_boards')
def pinterest_boards():
    """Displays all of user's boards from their pinterest"""

    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/', headers=headers, params=payload)
    boards_request = new_request.json()
    # FIX ME - do I still need enumerate?
    for board in boards_request['data']:
        url = board['url']
        url = url.split('/')
        board_name = url[-2]
        board['url'] = board_name

    return render_template('user_pinterest.html',
                           boards=boards_request,
                           first_name=session['first_name'])


# 12
@app.route('/pinterest_board_images/<url>')
def pinterest_board_images(url):
    """Displays pins from user chosen board that is on pinterest"""

    # import pdb; pdb.set_trace()

    user = User.query.filter(User.user_id == session['user_id']).first()
    username = user.username
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note', 'limit': 100}
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


# 13
@app.route('/save_board', methods=['POST'])
def save_board():
    """Saves board to Beautiful Lines"""

    board = request.form.get('board_url')
    user_id = session['user_id']
    username = session['username']

    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s' % (username, board), headers=headers, params=payload)
    board_request = new_request.json()

    new_board = route_functions.save_board_from_pinterest(board, board_request, user_id)

    session['board_id'] = new_board.board_id
    session['board_url'] = new_board.url_name

    # After saving the board, need to save the images that are on the board
    return flaskredirect('/save_images_on_board.json')


# 14
@app.route('/save_images_on_board.json')
def save_images_on_board():

    board_id = session['board_id']
    user = User.query.filter(User.user_id == session['user_id']).first()
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s/pins' % (session['username'], session['board_url']), headers=headers, params=payload)
    pins_request = new_request.json()
    all_pins = pins_request['data']

    board = Board.query.filter(Board.board_id == board_id).first()

    # if there are images, set board image to first image on board
    print '*******************************************************'
    print all_pins

    if all_pins:
        current_board = Board.query.filter(Board.board_id == board_id).first()
        current_board.image_url = all_pins[0]['image']['original']['url']
        print '*******************************************************'
        print current_board.image_url
        db.session.commit()

    route_functions.save_images_from_pinterest_board(headers, payload, pins_request, user, board_id)


    print '*******************************************************'
    print board_id

    return ('Board Saved')


#15
@app.route('/edit_board.json', methods=['POST'])
def edit_board():
    """Edits user board"""

    new_title = request.form.get('new_board_title')
    new_image_url = request.form.get('new_image_url')
    new_description = request.form.get('new_board_description')
    board_id = request.form.get('board_id')

    route_functions.edit_board_info(new_title, new_image_url, new_description, board_id)

    flash('Your board has been successfully edited.')

    return ('Board Edited')


# 16
@app.route('/delete_board.json', methods=['POST'])
def delete_board():
    """Deletes user board from blines db and associated images and tags that don't exist in other boards"""

    board_id = request.form.get('board_id')

    route_functions.delete_board_from_database(board_id)

    flash('Your board has been successfully deleted.')

    return ('Board Deleted')


# 17
@app.route('/save_image.json', methods=['POST'])
def save_image():
    """Saves image to Beautiful Lines Board"""

    board_id = request.form.get('board')
    pin_id = request.form.get('pin_id')
    image_id = request.form.get('image_id')

    route_functions.save_individual_images(board_id, pin_id, image_id)

    return ('Image Saved')


# 18
@app.route('/edit_image.json', methods=['POST'])
def edit_image():
    """Edit user image"""

    new_description = request.form.get('new_image_description')
    image_id = request.form.get('image_id')

    route_functions.edit_image_info(new_description, image_id)

    flash('Your image has been successfully edited.')

    return ('Image Edited')


# 19
@app.route('/delete_image.json', methods=['POST'])
def delete_image():
    """Deletes user image from blines association table, and from images table if no instances of it exist in association table"""

    board_id = request.form.get('board_id')
    image_id = request.form.get('image_id')

    route_functions.delete_image_from_db(board_id, image_id)

    flash('Your image has been successfully deleted.')

    return ('Image Deleted')


# 20
@app.route('/create_board')
def create_board():
    """Creates new board in blines db"""

    board_name = request.args.get('board_name')
    board_description = request.args.get('board_description')
    image_url = request.args.get('image_url')
    url_name = quote_plus('board_name')

    route_functions.create_board(board_name, board_description, image_url, url_name, session['user_id'])

    flash('Your board has been successfully created.')

    return flaskredirect('/boards')


# 21
@app.route('/create_image/<int:board_id>')
def create_image(board_id):
    """Creates new image in blines db"""

    image_url = request.args.get('image_url')
    description = request.args.get('image_description')

    route_functions.create_image(image_url, description, board_id, session['user_id'])

    flash('Your image has been successfully created.')

    return flaskredirect('/user_board_images/%s' % board_id)


# 22
@app.route('/study_board/<int:board_id>')
def study_board(board_id):
    """Displays pins from board chosen by user to study"""

    images = Board.query.get(board_id).images
    current_board = Board.query.filter(Board.board_id == board_id).first()

    print current_board
    print current_board.board_name
    print '****************************************************'

    return render_template('study.html',
                           images=images,
                           current_board=current_board)


# 23
@app.route('/study_images.json', methods=['POST'])
def study():
    """Sends json of images to js for Study Session"""

    board_id = request.form.get('board_id')
    images = Board.query.get(board_id).images
    list_of_image_urls = []

    for image in images:
        list_of_image_urls.append(image.original_url)

    return json.dumps(list_of_image_urls)


# 24
@app.route('/search_bl')
def show_bl_search():
    """Search user's images and display images related to user search terms"""

    user_search = request.args.get('images-search')

    images, boards = route_functions.search(user_search, 'all')

    return render_template('pinterest_board.html',
                           images=images,
                           boards=boards,
                           search=user_search)


# 25
@app.route('/search_user')
def show_user_search():
    """Search user's images and display images related to user search terms"""

    user_search = request.args.get('images-search')

    images, boards = route_functions.search(user_search, 'user')

    return render_template('pinterest_board.html',
                           images=images,
                           boards=boards,
                           search=user_search)

# 26
@app.route("/error")
def error():
    raise Exception("Error!")


# End Routes ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.debug = True

    connect_to_db(app, os.environ.get("DATABASE_URL"))

    # context = ('server-files/yourserver.crt', 'server-files/yourserver.key')
    # app.run(ssl_context=context)

    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
