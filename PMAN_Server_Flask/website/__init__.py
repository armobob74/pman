import pdb 
from .connection import Connection
from .pman_blueprints.aurora_pump import aurora_pump
from .pman_blueprints.aurora_valve import aurora_valve
from .pman_blueprints.release_scheduler import release_scheduler

from .views import views
from flask import Flask
from flask_cors import CORS
from .scheduler import init_scheduler
import json
import logging
import os
import sass

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

def create_app(pman_config_name):
    sass.compile(dirname=('./website/static/sass','./website/static/css'))
    app = Flask(__name__)
    CORS(app)
    pman_config_path = os.path.join('configs',pman_config_name)
    app.config['pman-config-path'] = pman_config_path
    with app.open_resource(pman_config_path) as f:
        app.config['pman-config'] = json.load(f)
    print("Loaded config:", pman_config_name)
    pman_config = app.config['pman-config']
    app.logger.setLevel(logging.DEBUG)
    for handler in create_handlers():
        app.logger.addHandler(handler)
    init_scheduler(app)
    app.connection = Connection(
            serial_port=pman_config['serial_port'],
            read_until=pman_config.get('read_until', None)
        )
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(aurora_valve)
    app.register_blueprint(aurora_pump)
    app.register_blueprint(release_scheduler)
    return app
