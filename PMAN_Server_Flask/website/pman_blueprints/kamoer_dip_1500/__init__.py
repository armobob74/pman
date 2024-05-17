from flask import current_app, request, Blueprint
import json
import pdb
from .command_formatting_playground import ModbusRTU
from math import log, floor
from ..utils import extract_pman_args 

default_addr = '1'

kamoer_peri = Blueprint('kamoer_peri',__name__, url_prefix='/pman/kamoer-peri')

@kamoer_peri.get('/')
def index():
    return "hi"

@kamoer_peri.post('/start')
@extract_pman_args
def start_pump(rpm, dir, addr):
    modbus = ModbusRTU(current_app.connection.serial)
    modbus.set_rpm(rpm, addr)
    if dir == 1:
        modbus.motor_clockwise(addr)
    else:
        modbus.motor_counterclockwise(addr)
    modbus.set_runtime(0, addr) # Set to 0 because we want pump to run indefinetly.
    modbus.motor_start(addr)
    return {'status': "ok", 'message': "Pump Started"}

@kamoer_peri.post('/stop')
@extract_pman_args
def stop_pump(addr):
    modbus = ModbusRTU(current_app.connection.serial)
    modbus.motor_stop(addr)
    return {'status': "ok", 'message': "Pump Stopped"}
