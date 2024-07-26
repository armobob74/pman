""" DCDLI V2 is a relay board controlled over RS485 """
import time
import random 
import pdb
from flask import current_app, Blueprint, jsonify
from minimalmodbus import InvalidResponseError
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

def execute_serial_action(action,args=[]):
    """ guarantees that the action is done, and redoes it if necessary """
    response_good = False
    while response_good != True:
        try:
            action(*args)
            response_good = True
        except:
            response_good = False
            print(f"Got bad checksum, trying again")
            time.sleep(random.random()/2) # the randomness prevents serial clogs

@dcdli_v2.route('/on', methods=['POST'])
@extract_pman_args
def relay_on(relay_name):
    rb = make_relay()
    idx = get_relay_idx(relay_name)
    execute_serial_action(rb.open_relay,[idx])
    return jsonify({'message':f'Relay {idx} ON', 'status':'ok'})

@dcdli_v2.route('/off', methods=['POST'])
@extract_pman_args
def relay_off(relay_name):
    rb = make_relay()
    idx = get_relay_idx(relay_name)
    execute_serial_action(rb.close_relay,[idx])
    return jsonify({'message':f'Relay {idx} OFF', 'status':'ok'})

@dcdli_v2.get('/status/<string:relay_name>')
def relay_status(relay_name):
    rb = make_relay()
    idx = get_relay_idx(relay_name)
    # status updates do not get the special execution function because I do not want
    # them to re-exeute in the event of a serial line collision
    try:
        return jsonify(rb.read_relay(idx))
    except InvalidResponseError: 
        return jsonify({'error': 'Invalid response from relay'}), 500

@dcdli_v2.get('/status')
def relay_status_all():
    rb = make_relay()
    # status updates do not get the special execution function because I do not want
    # them to re-exeute in the event of a serial line collision
    try:
        return jsonify(rb.read_all_relays())
    except InvalidResponseError: 
        return jsonify({'error': 'Invalid response from relays'}), 500

@dcdli_v2.route('/all-on', methods=['POST'])
def relay_all_on():
    rb = make_relay()
    rb.open_all()
    execute_serial_action(rb.open_all)
    return jsonify({'message':f'Relays all ON', 'status':'ok'})

@dcdli_v2.route('/all-off', methods=['POST'])
def relay_all_off():
    rb = make_relay()
    execute_serial_action(rb.close_all)
    return jsonify({'message':f'Relays all OFF', 'status':'ok'})

