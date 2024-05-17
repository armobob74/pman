from flask import current_app, request, Blueprint
import json
import pdb
from website.modbus import extract_data_cl
from math import log, floor
from ..utils import extract_pman_args 
from serial import SerialException

default_addr = '1'

kamoer_peri = Blueprint('kamoer_peri',__name__, url_prefix='/pman/kamoer-peri')

@kamoer_peri.errorhandler(SerialException)
def handle_serial_error(e):
    return {'status': "SerialException", 'message': f"{e}"}, 500

@kamoer_peri.get('/')
def index():
    return "hi"

@kamoer_peri.post('/start')
@extract_pman_args
def start_pump(addr, direction, rpm):
    addr = int(addr)
    addr = addr.to_bytes(1, byteorder='big')
    direction = int(direction)
    rpm = float(rpm)
    modbus = current_app.connection.modbus
    if direction == 1:
        modbus.motor_clockwise(addr)
    else:
        modbus.motor_counterclockwise(addr)
    modbus.set_runtime(0, addr) # Set to 0 because we want pump to run indefinetly.
    modbus.motor_start(addr)
    return {'status': "ok", 'message': "Pump Started"}

@kamoer_peri.post('/stop')
@extract_pman_args
def stop_pump(addr):
    addr = addr.to_bytes(1, byteorder='big')
    current_app.connection.modbus.motor_stop(addr)
    return {'status': "ok", 'message': "Pump Stopped"}

@kamoer_peri.get('/status')
def read_status():
    addr_str = request.args.get('addr')  
    addr_int = int(addr_str) 
    addr_bytes = addr_int.to_bytes(1, byteorder='big') 
    modbus = current_app.connection.modbus
    data = modbus.read_motor_status(addr_bytes) # error here? contains b''
    data2 = modbus.read_dir(addr_bytes)
    if(data != b'' and data2 != b''):
        data_int = extract_data_cl(data)
        data2_int = extract_data_cl(data2)
        if data_int == 1 and data2_int == 1:
            return {'status': "clockwise"}
        elif data_int == 1 and data2_int == 0:
            return {'status': "counterclockwise"}
    return {'status': "off"}
