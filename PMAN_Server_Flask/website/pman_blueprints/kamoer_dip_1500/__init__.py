from flask import current_app, request, Blueprint
import json
import pdb
from math import log, floor

default_addr = '1'
kamoer_peri = Blueprint('kamoer_peri',__name__, url_prefix='/pman/kamoer-peri')

@kamoer_peri.get('/')
def index():
    return "hi"
