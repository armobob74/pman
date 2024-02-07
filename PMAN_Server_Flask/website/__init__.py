from flask import Flask
import sass
from .views import views
import os
from .connection import Connection
import logging

LOG_DIR = 'logs'
INFO_FILE = 'info.log'
DEBUG_FILE = 'debug.log'

def create_handlers():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    debug_path = os.path.join(LOG_DIR, DEBUG_FILE)
    info_path = os.path.join(LOG_DIR, INFO_FILE)

    debug_handler = logging.FileHandler(debug_path)
    debug_handler.setLevel(logging.DEBUG)
    info_handler = logging.FileHandler(info_path)
    info_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)

    return [debug_handler, info_handler]

def create_app():
    sass.compile(dirname=('./website/static/sass','./website/static/css'))
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    for handler in create_handlers():
        app.logger.addHandler(handler)
    app.connection = Connection()
    app.register_blueprint(views, url_prefix='/')
    return app