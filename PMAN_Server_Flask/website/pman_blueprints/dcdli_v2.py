""" DCDLI V2 is a relay board controlled over RS485 """
import pdb
from flask import current_app, Blueprint, jsonify
from rs485_relay_board import RelayBoard
from .utils import extract_pman_args

dcdli_v2 = Blueprint('dcdli_v2', __name__, url_prefix='/pman/dcdli-v2')

# later perhaps expand? We can have these things wired in a bus easily.
ADDRESS = 1

def make_relay():
    serial_port = current_app.config['pman-config']['serial_port']
    rb = RelayBoard(serial_port, ADDRESS)
    return rb

def get_relay_idx(relay_name):
    relays = current_app.config['pman-config']['instrument_info']['relays']
    if relay_name not in relays:
        raise ValueError(f"Relay name {relay_name} not defined. Check spelling or update your config.")
    return relays[relay_name]

@dcdli_v2.route('/on', methods=['POST'])
@extract_pman_args
def relay_on(relay_name):
    rb = make_relay()
    idx = get_relay_idx(relay_name)
    rb.open_relay(idx)
    return jsonify({'message':f'Relay {idx} ON', 'status':'ok'})

@dcdli_v2.route('/off', methods=['POST'])
@extract_pman_args
def relay_off(relay_name):
    rb = make_relay()
    idx = get_relay_idx(relay_name)
    rb.close_relay(idx)
    return jsonify({'message':f'Relay {idx} OFF', 'status':'ok'})

@dcdli_v2.get('/status/<string:relay_name>')
def relay_status(relay_name):
    rb = make_relay()
    idx = get_relay_idx(relay_name)
    return jsonify(rb.read_relay(idx))

@dcdli_v2.get('/status')
def relay_status_all():
    rb = make_relay()
    ret = rb.read_all_relays()
    return jsonify(ret)
