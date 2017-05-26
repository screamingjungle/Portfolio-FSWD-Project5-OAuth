from flask import Flask
from flask_seasurf import SeaSurf

app = Flask(__name__)
csrf = SeaSurf(app)

import shopfront.handlers.base
import shopfront.handlers.images
import shopfront.handlers.homepage
import shopfront.handlers.item
import shopfront.handlers.category
import shopfront.handlers.collection
import shopfront.handlers.tag
import shopfront.handlers.search
import shopfront.handlers.user
import shopfront.handlers.message
import shopfront.handlers.json_endpoints
import shopfront.handlers.login
import shopfront.handlers.oauth
