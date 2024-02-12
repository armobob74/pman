from flask import current_app, request, Blueprint
from .utils import extract_pman_args

RESPOSE_LEN = 8 # number of response bytes expected

aurora_pump = Blueprint('aurora_pump',__name__, url_prefix='/pman/aurora-pump')

def format_command(data):
    """ Doesn't include R, which is needed to run action commands """
    return f'/1{data}\r'.encode()

def vol_to_steps(volume):
    """ 6000 steps == 25 mL """
    steps_per_vol = 6000 / 25
    steps = volume * steps_per_vol
    return steps

def transfer_command_string(from_port, to_port, volume):
    """
    Copied from Hamilton tbh
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


@aurora_pump.route("/transfer", methods=["POST"])
@extract_pman_args
def switch_to_port(from_port, to_port, volume):
    current_app.logger.debug(f"Called aurora transfer({port_number})")


    command = format_command(data=command_string) 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':response.decode()}

