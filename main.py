"""
Main script used to start the application.
"""
import os.path

from books import app
from books.db.database_setup import Base, catalog_create
from books.db.database_seed import db_seed

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
    
    app.config['NAME'] = 'book'
    
    app.config['DATABASE_TYPE'] = 'sqlite'
    app.config['DATABASE_NAME'] = '%scatalog' % app.config['NAME']
    app.config['DATABASE_URL'] = '%s:///%s.db' % (app.config['DATABASE_TYPE'], app.config['DATABASE_NAME'])

    app.secret_key = 'test_secret_key'

    app.config['PAGE_LIMIT'] = 2


    if app.config['DATABASE_TYPE'] == 'sqlite':
        if os.path.isfile('%s.db' % app.config['DATABASE_NAME']) is False:
            catalog_create(app.config['DATABASE_URL'])
            db_seed()

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
