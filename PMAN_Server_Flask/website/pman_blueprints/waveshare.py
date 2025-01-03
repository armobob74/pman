import os
import threading
import minimalmodbus
import serial
import time
import json
from flask import current_app, Blueprint, jsonify
from .utils import extract_pman_args

def load_json():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_folder = os.path.join(script_dir, '..', 'configs')
    config_file = os.path.join(config_folder, 'waveshare_relay_win.json')    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"The config file does not exist at: {config_file}")
    
    with open(config_file, 'r') as file:
        config = json.load(file)
    
    return config

jsonl = load_json()

PORT = jsonl['serial_port']
WAVESHARE_ID = jsonl["instrument_info"]["ID"]    
TOTAL_RELAYS = jsonl["instrument_info"]["relays"]
instrument = minimalmodbus.Instrument(PORT, WAVESHARE_ID)
instrument.serial.baudrate = 9600                  
instrument.serial.timeout = 1

waveshare = Blueprint('waveshare',__name__, url_prefix='/pman/waveshare')

@waveshare.route("/on", methods=["POST"])
@extract_pman_args
def turn_on(num):
    register_address = num - 1
    instrument.write_bit(register_address, True, functioncode=5)
    return jsonify({"status": f"Relay {num} turned ON"})

@waveshare.route("/off", methods=["POST"])
@extract_pman_args
def turn_off(num):
    register_address = num - 1
    instrument.write_bit(register_address, False, functioncode=5)
    return jsonify({"status": f"Relay {num} turned ON"})

@waveshare.route("/toggle", methods=["POST"])
@extract_pman_args
def toggle_channel(num):
    register_address = num - 1
    current_state = read_channel(num)
    new_state = not current_state
    instrument.write_bit(register_address, new_state, functioncode=5)
    return jsonify({"status": f"Relay {num} toggled"})

def read_channel(num):
    register_address = num - 1
    current_state = instrument.read_bit(register_address, functioncode=1)
    return current_state

@waveshare.route("/all_status")
def read_all():
    relay_status = {}
    for relay_index in range(TOTAL_RELAYS):
        status = read_channel(relay_index + 1)
        relay_status[f"{relay_index + 1}"] = "On" if status else "Off"
    return relay_status
