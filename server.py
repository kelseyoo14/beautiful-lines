import requests
import os
from flask import Flask, request, render_template, redirect
# from OpenSSL import SSL

pinterest_client_id = os.environ['PINTEREST_CLIENT_ID']
access_token = os.environ['ACCESS_TOKEN']
# headers = {'Authorization': 'Bearer %s' % access_token}

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"


@app.route('/')
def homepage():
    """Website Homepage/Welcome"""

    return render_template('homepage.html')


@app.route('/testing_request')
def testing_request():
    """render new html template!"""

    # Start here with your access token.
    headers = {'Authorization': 'Bearer %s' % access_token}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/', headers = headers)
    new_request_edited = new_request.json()

    return render_template('testserverpage.html',
                            new_request=new_request,
                            new_request_edited=new_request_edited)


@app.route('/login', methods=['POST'])
def login():
    """Log in User"""

    return render_template('dashboard.html')



@app.route('/dashboard')
def dashboard():
    """User dashboard that lists there boards"""

    headers = {'Authorization': 'Bearer %s' % access_token}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/', headers = headers)
    boards_request = request.json()

    return render_template('dashboard.html',
                            boards_request=boards_request)

@app.route('/show_board')
def show_board():
    """Displays user board"""

    headers = {'Authorization': 'Bearer %s' % access_token}
    new_request = requests.get('https://api.pinterest.com/v1/me/boards/painting/pins', headers = headers)
    pins_request = new_request.json()

    return render_template('user_board.html',
                            pins_request=pins_request)


@app.route('/search')
def show_search():
    """Search and display pins related to user search terms"""

    return render_template('search.html')


# @app.route('study_mode')
# def study_mode():
#     """Should this be a model??? User setup study mode. Displays user picked images at user set intervals"""




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    # connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    context = ('server-files/yourserver.crt', 'server-files/yourserver.key')
    app.run(ssl_context=context)
