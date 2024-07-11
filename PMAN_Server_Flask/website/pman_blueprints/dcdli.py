from flask import current_app, Blueprint, jsonify
from .utils import extract_pman_args

dcdli = Blueprint('dcdli', __name__, url_prefix='/pman/dcdli')

@dcdli.post('/on')
@extract_pman_args
def turn_on_pin(pinNum):
    cmd = f'/I{pinNum}\r'
    current_app.connection.send(cmd.encode(), immediate=True)
    return jsonify({'status': 'ON', 'message': f'Pin {pinNum} turned ON'})

@dcdli.post('/off')
@extract_pman_args
def turn_off_pin(pinNum):
    cmd = f'/O{pinNum}\r'
    current_app.connection.send(cmd.encode(), immediate=True)
    return jsonify({'status': 'OFF', 'message': f'Pin {pinNum} turned OFF'})

@dcdli.post('/status')
@extract_pman_args
def get_pin_status(pinNum):
    cmd = f'/S{pinNum}\r'
    response = current_app.connection.send(cmd.encode(), immediate=True)
    if response:
        response_str = response.decode().strip()
        st = ''
        if response_str == '1':
            st = "ON"
        elif response_str == '0':
            st = "OFF"
        return jsonify({'status': 'ok', 'message': st})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to get status'})
    
@dcdli.get('/get_all_status')
def get_pin_status_all():
    pins={}
    cmd = '/S0\r'
    response = current_app.connection.send(cmd.encode(), immediate=True)
    response_str = response.decode().strip()
    pinz = current_app.config['pman-config']['instrument_info']['pins']
    c = 0
    for pin in pinz:
        st = ''
        if response_str[c] == '1':
            st = "ON"
        elif response_str[c] == '0':
            st = "OFF"
        else:
            st = "Failed to get Status"
        pins[pin] = st
        c +=1
    
    return jsonify(pins)