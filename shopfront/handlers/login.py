from flask import render_template, session

from shopfront import app
from shopfront.handlers.functions import get_nonce

@app.route('/login')
def showLogin():
    """
    Renders the login page
    """
    session['state'] = get_nonce()
    return render_template('login.html', STATE=session['state'])
