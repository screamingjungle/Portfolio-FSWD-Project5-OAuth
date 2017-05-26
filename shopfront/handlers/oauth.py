from flask import request, redirect, url_for, flash, make_response
from flask import session as login_session

from shopfront import app
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

from shopfront.handlers.functions import userCreate, userIdGet, userGroupGet, reset_session

APPLICATION_NAME = 'UdacityItemCatalog'

# google
GOOGLE_KEY = json.loads(
    open('client_secrets.json', 'r').read())['web']
GOOGLE_CLIENT_ID = GOOGLE_KEY['client_id']

#facebook
FACEBOOK_KEY = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']
FACEBOOK_APP_ID = FACEBOOK_KEY['app_id']
FACEBOOK_APP_SECRET = FACEBOOK_KEY['app_secret']

# Make CLIENT IDs available to templates.
app.jinja_env.globals['GOOGLE_CLIENT_ID'] = GOOGLE_CLIENT_ID
app.jinja_env.globals['FACEBOOK_APP_ID'] = FACEBOOK_APP_ID

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Connects to your Gmail account with OAuth2
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    h = httplib2.Http()
    content = h.request(url, 'GET')[1]
    data = json.loads(content.decode('utf-8'))

    # If there was an error in the access token info, abort.
    if data.get('error') is not None:
        response = make_response(json.dumps(data.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if data['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if data['issued_to'] != GOOGLE_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.json
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    if data['name']:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email'].split("@")[0]
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if user exists. It not, create a new one
    user_id = userIdGet(login_session['email'])
    if not user_id:
        coll = userCreate(login_session)
        user_id = next(iter(coll))

        if coll[user_id]:
            print("user Created = %s" % coll[user_id])
        else:
            reset_session()
            flash('New User Registration Failed!')
            return redirect(url_for('showLogin'))

    login_session['user_id'] = user_id
    login_session['group'] = userGroupGet(user_id)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """
    Logout of your gmail account
    """
    credentials = login_session.get('credentials')
    access_token = credentials
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        flash("You have signed out")
        return "Logout successul."
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Facebook OAuth
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Connects to your Facebook account with OAuth
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode('utf-8')

    url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
        'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
        '&fb_exchange_token=%s') % (FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, 
        access_token)
    h = httplib2.Http()

    content = h.request(url, 'GET')[1]
    data = json.loads(content.decode('utf-8'))

    if not 'access_token' in data:
        reset_session()
        flash('Facebook Login OAuth Failed!')
        return redirect(url_for('showLogin'))

    # userinfo_url = "https://graph.facebook.com/v2.9/me"
    token = 'access_token=' + data['access_token']
    fb_fields = 'name,id,email,picture.type(large)'

    url = 'https://graph.facebook.com/v2.9/me?%s&fields=%s' % (token, fb_fields)

    h = httplib2.Http()
    content = h.request(url, 'GET')[1]
    data = json.loads(content.decode('utf-8'))

    if not 'name' in data:
        reset_session()
        flash('Facebook Login Failed!')
        return redirect(url_for('showLogin'))

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
    try:
        login_session['picture'] = data["picture"]["data"]["url"]
    except:
        login_session['picture'] = ''

    # Check if user exists. It not, create a new one
    user_id = userIdGet(login_session['email'])
    if not user_id:
        coll = userCreate(login_session)
        user_id = next(iter(coll))

        if coll[user_id]:
            print("user Created = %s" % coll[user_id])
        else:
            reset_session()
            flash('New User Registration Failed!')
            return redirect(url_for('showLogin'))

    login_session['user_id'] = user_id
    login_session['group'] = userGroupGet(user_id)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """
    Logout of your Facebook account
    """
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    flash("You have signed out")
    return "You've been logged out"


@app.route('/disconnect')
def disconnect():
    """
    Process the gdisconnect or fbdisconnect methods to log out of
    their respective accounts
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        elif login_session['provider'] == 'facebook':
            fbdisconnect()

        flash("Session has been reset")
    else:
        flash("You are not logged in")

    reset_session()
    return redirect(url_for('homepage'))
