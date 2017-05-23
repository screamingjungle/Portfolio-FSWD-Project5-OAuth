# Reference:
# https://github.com/SteveWooding/fullstack-nanodegree-vm/blob/master/vagrant/catalog/catalog/connect_to_database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shopfront import app
from shopfront.db.database_setup import Base


def connect_to_database():
    """Connect to database and return a session object"""
    engine = create_engine(app.config['DATABASE_URL'])
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session

def ilike_needle(needle):
    """
    Format needle for DB Like check (e.g. for Item.Tags search)
    """
    if '*' in needle or '_' in needle:
        looking_for = needle.replace('_', '__')\
                            .replace('*', '%')\
                            .replace('?', '_')
    else:
        looking_for = '%{0}%'.format(needle)
    return looking_for