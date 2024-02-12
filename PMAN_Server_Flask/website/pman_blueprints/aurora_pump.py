from flask import current_app, request, Blueprint
import pdb
from .utils import extract_pman_args


ADDR = '1'
aurora_pump = Blueprint('aurora_pump',__name__, url_prefix='/pman/aurora-pump')

def format_command(data):
    """ Doesn't include R, which is needed to run action commands """
    current_app.logger.debug(f"Formatting command data: {data}")
    return f'/{ADDR}{data}\r'.encode()

resolution = 6000 # steps
max_draw_volume = 25 #mL
syringe_size = 25 #mL
def vol_to_steps(volume):
    """ 6000 steps == 25 mL """
    steps = volume * resolution / syringe_size
    return int(steps)

max_height = vol_to_steps(max_draw_volume)
def transfer_command_string(from_port, to_port, volume):
    """
    Copied from Hamilton server tbh
    """
    full_transfers = ''
    if volume > max_draw_volume:
        loops = int(volume // max_draw_volume)
        full_transfers = f'gI{from_port}A{max_height}O{to_port}A0G{loops}'

    remainder = volume % max_draw_volume
    partial_transfer_steps = int((remainder / syringe_size) * resolution)
    if remainder == 0:
        partial_transfers = ''
    else:
        partial_transfers = f"I{from_port}A{partial_transfer_steps}O{to_port}A0"
    return partial_transfers + full_transfers + 'R'

def parse_response(response_bytes):
    response_data = response_bytes[1:-3].decode()
    current_app.logger.debug(f"Got response: {response_data}")
    return response_data

@aurora_pump.route("/transfer", methods=["POST"])
@extract_pman_args
def switch_to_port(from_port, to_port, volume):
    current_app.logger.debug(f"Called aurora transfer({from_port, to_port, volume})")
    volume = float(volume)
    command_string = transfer_command_string(from_port, to_port, volume)
    command = format_command(data=command_string) 

    # first byte of response can't be decoded in utf-8
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/set-speed-code", methods=["POST"])
@extract_pman_args
def set_speed_code(speed_code):
    current_app.logger.debug(f"Called aurora set speed-code ({speed_code})")
    command = format_command(data=f'S{speed_code}R')
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}
