from flask import render_template
from flask import session as login_session
import random
import string

from shopfront import app
from shopfront.db.database_connect import connect_to_database


@app.route('/login')
def showLogin():
    """
    Renders the login page
    """
    login_session['state'] = get_nonce()
    return render_template('login.html', STATE=login_session['state'])


def get_nonce():
    """
    Returns a nonce value to be used as an anti-CSRF token.
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))
