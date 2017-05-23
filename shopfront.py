"""
Main script used to start the application.
"""
import os.path

from shopfront import app
from shopfront.db.database_setup import Base, catalog_create
from shopfront.db.database_seed import db_seed

from flask import Flask
#import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# http://stackoverflow.com/questions/38523303/how-to-reload-a-flask-app-each-time-its-accessed/38524695#38524695
# This is used to refresh the server on template (html) changes
def before_request():
    app.jinja_env.cache = {}

if __name__ == '__main__':
    app.before_request(before_request)

    app.config['NAME'] = 'shopfront'

    app.config['DATABASE_TYPE'] = 'sqlite'
    app.config['DATABASE_NAME'] = '%scatalog' % app.config['NAME']
    app.config['DATABASE_URL'] = '%s:///%s.db' % (app.config['DATABASE_TYPE'], app.config['DATABASE_NAME'])

    app.secret_key = 'test_secret_key'

    app.config['PAGE_LIMIT'] = 35
    app.config['MIN_FIELD_LENGTH'] = 3

    # number of characters visible in
    app.jinja_env.globals['MAX_ITEM_DESCRIPTION_CHARS'] = 165

    # allow conventional login (not oauth2)
    app.jinja_env.globals['ALLOW_NONOAUTH_LOGIN'] = False
    app.jinja_env.globals['ALLOW_OAUTH_LOGIN'] = True


    if app.config['DATABASE_TYPE'] == 'sqlite':
        if os.path.isfile('%s.db' % app.config['DATABASE_NAME']) is False:
            catalog_create(app.config['DATABASE_URL'])
            db_seed()

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
