import requests
import os
from urllib import urlencode
from flask import Flask, request, render_template, session
# redirect was getting overwritten somehow - still need to figure out why
# solution for now is to import separately as 'flaskredirect'
from flask import redirect as flaskredirect
# import flask
# from OpenSSL import SSL

CLIENT_ID = os.environ['PINTEREST_CLIENT_ID']
APP_SECRET = os.environ['PINTEREST_APP_SECRET']

# My Global access_token. Need to use session to store user's access token
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
# headers = {'Authorization': 'Bearer %s' % access_token}

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"


@app.route('/')
def homepage():
    """Website Homepage/Welcome"""

    return render_template('homepage.html')


# OAuth and Log In Start ------------------------------------------------------------

@app.route('/login')
def login():
    """OAuth - Redirect user to log in"""

    # Data that pinterest requests is sent
    auth_data = {
                # Pinterest says to use 'code'
                'response_type': 'code',
                # Route I want Pinterest to go to once user logs in and Pinterest processes the log in
                # Need to remember to register this redirect route on pinterest app!
                'redirect_uri': 'https://localhost:5000/get_access_token',
                # My apps's client_id, so pinterest know's who's redirecting the user to their page
                'client_id':CLIENT_ID,
                # What I want to be able to do with user's account
                'scope': 'read_public,write_public',
                # Note for myself
                'state': 'Random!'
                }

    url = 'https://api.pinterest.com/oauth?'

    # urlencode changes auth_data into url string, redirect needs url, can't take params
    # need to import urlencode from urllib
    full_url = url + urlencode(auth_data)

    return flaskredirect(full_url)


@app.route('/get_access_token')
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

    # Need to store access_token in session so that I can have global use
    session['user_token'] = access_token

    # for test request
    headers = {'Authorization': 'Bearer %s' % access_token}

    # test request using access_token
    new_request = requests.get('https://api.pinterest.com/v1/me', headers=headers)

    return render_template('search.html')

# OAuth and Log In End ---------------------------------------------------------------



@app.route('/testing_request')
def testing_request():
    """testing route for making requests to Pinterest"""

    # https://api.pinterest.com/v1/me/pins/?
    # access_token=<YOUR-ACCESS-TOKEN>
    # &fields=id,creator,note
    # &limit=1

    headers = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
    payload = {'fields': 'id,note,image', 'limit': 1}

    new_request = requests.get('https://api.pinterest.com/v1/me/pins/', headers=headers, params=payload)
    new_request_edited = new_request.json()

    return render_template('testserverpage.html',
                            new_request=new_request,
                            new_request_edited=new_request_edited,
                            client_id=CLIENT_ID)


# Don't need anymore???
# @app.route('/login', methods=['POST'])
# def login():
#     """Log in User"""

#     # first_name = request.form.get('firstname')
#     # last_name = request.form.get('lastname')

#     # user = User(first_name=)

#     return render_template('dashboard.html')



@app.route('/dashboard')
def dashboard():
    """User dashboard that lists there boards"""

    headers = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
    payload = {'fields': 'id,name,image,description,url'}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/', headers = headers, params=payload)
    boards_request = new_request.json()
    for index, board in enumerate(boards_request['data']):
        url = board['url']
        url = url.split('/')
        board_name = url[-2]
        board['url'] = board_name
        # boards_request['data'][index]['url'] = board_name


    return render_template('dashboard.html',
                            boards_request=boards_request)

@app.route('/show_board/<url>')
def show_board(url):
    """Displays user board"""

    headers = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
    payload = {'fields': 'id,note,image'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/kelseyoo14/%s/pins' % (url), headers=headers, params=payload)
    pins_request = new_request.json()
    print url

    return render_template('user_board.html',
                            pins_request=pins_request)


# Test route
@app.route('/test_show_board/')
def test_show_board():
    """test - Displays user board"""


    headers = {'Authorization': 'Bearer %s' % ACCESS_TOKEN}
    payload = {'fields': 'id,note,image'}
    new_request = requests.get('https://api.pinterest.com/v1/boards/kelseyoo14/environments/pins', headers=headers, params=payload)
    pins_request = new_request.json()

    return render_template('user_board.html',
                            pins_request=pins_request)


@app.route('/search')
def show_search():
    """Search and display pins related to user search terms"""

    return render_template('search.html')


# @app.route('/study')
# def study_mode():
#     """Displays pins from board chosen by user to set time intervals to study"""

#     return render_template('study.html')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    context = ('server-files/yourserver.crt', 'server-files/yourserver.key')
    app.run(ssl_context=context)
