import pdb 
from .connection import Connection
from .pman_blueprints.aurora_pump import aurora_pump
from .pman_blueprints.aurora_valve import aurora_valve
from .pman_blueprints.release_scheduler import release_scheduler
from .pman_blueprints.kamoer_dip_1500 import kamoer_peri
from .pman_blueprints.dcdli import dcdli
from .pman_blueprints.dcdli_v2 import dcdli_v2

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
    # used to alert user of improper format
    # usually front end handles this, but sometimes only backend knows when format is wrong
    # e.g. when the backend dateutil parser can't parse a time
    app.config['bad-format-text'] = ' -- BAD FORMAT' 
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

    # register only the blueprints that the config says are necesary
    # we also check for any special config variables that the blueprints may need
    optional_blueprints = pman_config.get('blueprints',[])
    for b in optional_blueprints:
        try:
            eval(f'app.register_blueprint({b})')
        except NameError:
            raise NameError(f"You're trying to register a blueprint that you haven't imported: {b}")
    return app

def register_aurora_pump_blueprint(app):
    """ Aurora pump blueprint requires some special config variables to be set. Let's check for them in __init__ instead of waiting until function call time. """
    pman_config = app.config['pman-config']
    instrument_info = pman_config.get('instrument_info',{})
    # instrument info is information about the physical instrument itself, rather than pman networking info
    if not instrument_info:
        raise ValueError('Expected "instrument_info" section in pman_config for Aurora Pump blueprint')

    required_keys = ["num_valve_ports", "resolution", "syringe_size"]
    for key in required_keys:
        if not key in instrument_info:
            raise ValueError(f'Expected "{key}" key in "instrument_info" for Aurora Pump blueprint')

    app.register_blueprint(aurora_pump)
