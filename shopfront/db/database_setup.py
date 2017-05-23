import os

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


# Create absolute path variables.
WORKING_DIRECTORY = os.path.dirname(__file__)
RELATIVE_IMAGE_DIRECTORY = 'img'
ABSOLUTE_IMAGE_DIRECTORY = os.path.join(WORKING_DIRECTORY, '../img')

# Define constants.
ALLOWED_IMAGE_EXTENSIONS = set(['jpg', 'png'])
DEFAULT_IMAGE = '/static/default.png'

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    picture = Column(String(256))
    group = Column(String(10))
    enabled = Column(Boolean, default=True)
    collections = relationship("Collection", backref="usr")
    categories = relationship("Category", backref="usr")
    items = relationship("Item", backref="usr")
    provider = Column(String(20))
    passwd = Column(String(20))


class Collection(Base):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(4096))
    seo_url = Column(String(256))
    enabled = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    items = relationship("Item", backref="coll")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(4096))
    seo_url = Column(String(256))
    enabled = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User")

    items = relationship("Item", backref="cat")


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    meta_description = Column(String(1024))
    description = Column(String(4096))
    price = Column(Float)
    real_price = Column(Float)
    currency = Column(String(3), default='GBP')
    quantity = Column(Integer, default=0)
    image_url = Column(String(256))
    seo_url = Column(String(256))
    tags = Column(String(256))
    enabled = Column(Boolean, default=False)
    created = Column(DateTime, default=func.now())
    updated = Column(DateTime, default=func.now())
    collection_id = Column(Integer, ForeignKey('collections.id'))
    collection = relationship(Collection)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return data in serialized format"""
        return {
            'name': self.name,
            'meta_description': self.meta_description,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'image_url': self.image_url,
            'seo_url': self.seo_url,
            'category_id': self.category_id,
            'category_name': self.cat.name,
            'collection_id': self.collection_id,
            'collection_name': self.coll.name,
            'user_id': self.user_id,
            'user_name': self.usr.name,
        }

    @property
    def serializeJson(self):
        """Return serialized data for insertion into menu search feature
           (or external API call)"""
        return {
            'name': self.name,
            'description': self.meta_description,
            'id': self.id,
            'price': self.price,
            'html_url': '/p/%s' % self.seo_url,
            'category_id': self.category_id,
            'category_name': self.cat.name,
            'collection_id': self.collection_id,
            'collection_name': self.coll.name,
            'user_id': self.user_id,
            'user_name': self.usr.name,
        }

    @staticmethod
    def is_legal_image_file(filename):
        """Returns true if image file is of a legal file type."""
        return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS )


    def save_image(self, file):
        """Save uploaded image to disk and set item's image_url field.
           If file is blank or illegal, and this is a brand new item,
           then set the item image_url field to DEFAULT_IMAGE."""
        if file and self.is_legal_image_file(file.filename):
            self.delete_image()
            filename, extension = os.path.splitext(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = '%s-%s%s' % (self.id, timestamp, extension.lower())
            absolute_path = os.path.join(ABSOLUTE_IMAGE_DIRECTORY, filename)
            file.save(absolute_path)
            relative_path = os.path.join(RELATIVE_IMAGE_DIRECTORY, filename)
            self.image_url = '/' + relative_path
        else:
            if self.image_url is None:
                self.image_url = DEFAULT_IMAGE

    def delete_image(self):
        """Delete image file from disk, if exists."""
        if self.image_url and self.image_url != DEFAULT_IMAGE:
            os.remove(os.path.join(ABSOLUTE_IMAGE_DIRECTORY, self.image_url[1:]))

def catalog_create(db_url='sqlite:///catalog.db'):
    """Create the SQLlite database"""
    try:
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        print("DB successfully created")
    except:
        print("DB creation FAILED")
