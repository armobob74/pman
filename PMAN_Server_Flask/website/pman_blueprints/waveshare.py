import os
import threading
import minimalmodbus
import serial
import time
import json
from flask import current_app, Blueprint, jsonify
from .utils import extract_pman_args

waveshare = Blueprint('waveshare',__name__, url_prefix='/pman/waveshare')

@waveshare.route("/on", methods=["POST"])
@extract_pman_args
def turn_on(num):
    current_app.connection.waveshare.open_relay(num)
    return jsonify({"status": f"Relay {num} turned ON"})

@waveshare.route("/off", methods=["POST"])
@extract_pman_args
def turn_off(num):
    current_app.connection.waveshare.close_relay(num)
    return jsonify({"status": f"Relay {num} turned ON"})

@waveshare.route("/toggle", methods=["POST"])
@extract_pman_args
def toggle_channel(num):
    current_state = current_app.connection.waveshare.read_relay(num)
    new_state = not current_state
    current_app.connection.waveshare.instrument.write_bit(num-1, new_state, functioncode=5)
    return jsonify({"status": f"Relay {num} toggled"})

@waveshare.route("/all_status")
def read_all():
    num_relays = current_app.config.get('pman_config', {}).get('instrument_info', {}).get('relays', 16)
    rm = current_app.connection.waveshare
    relay_status = {i:('On' if rm.read_relay(i) else 'Off') for i in range(1,num_relays+1)}
    return relay_status
