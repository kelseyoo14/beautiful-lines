from model import User, Board, BoardImage, Image, ImageTag, Tag, connect_to_db, db
import requests
import os
from urllib import urlencode
from flask import Flask, request, render_template, session
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
def homepage():
    """Website Homepage/Welcome"""

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
                'client_id':CLIENT_ID,
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

    # print '--------------------USER INFO RESPONSE-----------------------'
    # print user_info

    # Query to check if user exists in the db
    user_exists = User.query.filter(User.pinterest_user_id == user_info['data']['id']).first()

    if user_exists:
        session['user_id'] = user_exists.user_id
        session['username'] = user_exists.username
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
        # print new_user

        # Add user_id and access_token to session for global use
        session['user_id'] = new_user.user_id
        session['username'] = new_user.username
        session['access_token'] = new_user.access_token

        print

    return render_template('search.html')

# OAuth and Log In End ---------------------------------------------------------------

# 4
@app.route('/logout')
def logout():
    session.clear()
    print "LOGGED OUT"

    return render_template('homepage.html')

# 5
@app.route('/dashboard')
def dashboard():
    """User dashboard that lists user's boards saved to blines db"""
    user_boards = Board.query.filter(Board.user_id == session['user_id']).all()


    return render_template('dashboard.html',
                            user_boards=user_boards)

# 6
@app.route('/user_pinterest')
def user_pinterest():
    """Displays user's boards from their pinterest"""

    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/', headers=headers, params=payload)
    boards_request = new_request.json()
    for index, board in enumerate(boards_request['data']):
        url = board['url']
        url = url.split('/')
        board_name = url[-2]
        board['url'] = board_name

    # print boards_request
        # boards_request['data'][index]['url'] = board_name

    return render_template('user_pinterest.html',
                            boards_request=boards_request)

# 7
@app.route('/show_board/<url>')
def show_board(url):
    """Displays user board"""

    user = User.query.filter(User.user_id == session['user_id']).first()
    username = user.username
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s/pins' % (username, url), headers=headers, params=payload)
    pins_request = new_request.json()
    print pins_request

    return render_template('user_board.html',
                            pins_request=pins_request)

# 8
@app.route('/save_board/<board>/')
def save_board(board):
    """Saves board to Beautiful Lines"""
    print board
    print '--------------------------------------'

    username = session['username']
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s' % (username, board), headers=headers, params=payload)
    board_request = new_request.json()
    print board_request
    print '---------------------------'

    pinterest_board_id = board_request['data']['id']
    board_name = board_request['data']['name']
    board_description = board_request['data']['description']
    image_url = board_request['data']['image']['60x60']['url']

    # Create new_board for db
    new_board = Board(pinterest_board_id=pinterest_board_id,
                      url_name=board,
                      board_name=board_name,
                      board_description=board_description,
                      image_url=image_url,
                      user_id=session['user_id'])

    db.session.add(new_board)
    db.session.commit()

    session['board_url'] = new_board.url_name

    return flaskredirect('/save_images_on_board')

# 9
# FIX ME - save all images on a board that is saved
@app.route('/save_images_on_board')
def save_images_on_board():

    user = User.query.filter(User.user_id == session['user_id']).first()
    username = user.username
    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/%s/%s/pins' % (username, session['board_url']), headers=headers, params=payload)
    pins_request = new_request.json()

    # make for loop to save each image in pins_request['data']
    for pin in pins_request['data']:
        pinterest_image_id = pin['id']
        original_url = pin['image']['original']['url']
        pinterest_url = pin['url']
        description = pin['note']

        # Create new_board for db
        new_image = Image(pinterest_image_id=pinterest_image_id,
                          original_url=original_url,
                          pinterest_url=pinterest_url,
                          description=description)

        db.session.add(new_image)

    db.session.commit()

    return flaskredirect('/user_pinterest')

# 10
@app.route('/delete_board/<board_id>')
def delete_board(board_id):
    """Deletes user board from blines db"""

    Board.query.filter(Board.board_id == board_id).delete()
    db.session.commit()

    return flaskredirect('/dashboard')

# 11
@app.route('/save_image/<pin_id>')
def save_image(pin_id):
    """Saves image to Beautiful Lines"""
    print pin_id
    print '--------------------------------------'

    headers = {'Authorization': 'Bearer %s' % session['access_token']}
    payload = {'fields': 'id,url,board,image,note'}
    new_request = requests.get('https://api.pinterest.com/v1/pins/%s' % (pin_id), headers=headers, params=payload)
    pin_request = new_request.json()
    print pin_request
    print '---------------------------'


    pinterest_image_id = pin_request['data']['id']
    original_url = pin_request['data']['image']['original']['url']
    pinterest_url = pin_request['data']['url']
    description = pin_request['data']['note']

    # Create new_board for db
    new_image = Image(pinterest_image_id=pin_id,
                      original_url=original_url,
                      pinterest_url=pinterest_url,
                      description=description)

    print new_image

    db.session.add(new_image)
    db.session.commit()

    return flaskredirect('/user_pinterest')


#     new_image = Image()



# @app.route('/search')
# def show_search():
#     """Search Pinterest(?) and display pins related to user search terms"""

#     return render_template('search.html')


# @app.route('/study')
# def study_mode():
#     """Displays pins from board chosen by user to set time intervals to study"""

#     return render_template('study.html')




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
