import requests
import os
from flask import Flask, request, render_template, redirect
# from OpenSSL import SSL

CLIENT_ID = os.environ['PINTEREST_CLIENT_ID']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
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


@app.route('/login', methods=['POST'])
def login():
    """Log in User"""

    # first_name = request.form.get('firstname')
    # last_name = request.form.get('lastname')

    # user = User(first_name=)

    return render_template('dashboard.html')



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

@app.route('/test_show_board/')
def test_show_board():
    """Displays user board"""


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
