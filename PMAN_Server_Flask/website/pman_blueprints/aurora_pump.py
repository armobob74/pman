from flask import current_app, request, Blueprint
import pdb
from math import log
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
    steps = float(volume) * resolution / syringe_size
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
    # first byte can not be decoded in utf-8
    response_data = response_bytes[1:-3].decode()
    current_app.logger.debug(f"Got response: {response_data}")
    return response_data

def is_busy():
    command = format_command('Q')
    response = current_app.connection.send(command, immediate=True)
    response = parse_response(response)
        
    if '@' in response:
        current_app.logger.debug(f"Determined pump is busy")
        return True
    elif '`' in response:
        current_app.logger.debug(f"Determined pump is NOT busy")
        return False
    else:
        errormsg = "Pump responded to query incorrectly -- is it busy or not? (check debug log)"
        current_app.logger.error(errormsg)
        raise ValueError(errormsg)

@aurora_pump.route("/transfer", methods=["POST"])
@extract_pman_args
def transfer(from_port, to_port, volume):
    current_app.logger.debug(f"Called aurora transfer({from_port, to_port, volume})")
    volume = float(volume)
    command_string = transfer_command_string(from_port, to_port, volume)
    command = format_command(data=command_string) 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/set-velocity", methods=["POST"])
@extract_pman_args
def set_velocity(velocity):
    """ Set max velocity in mL/min """
    current_app.logger.debug(f"Called aurora set velocity ({velocity})")
    velocity_steps_per_min = vol_to_steps(float(velocity))
    velocity_steps_per_sec = int(velocity_steps_per_min // 60)
    command = format_command(data=f'V{velocity_steps_per_sec}R')
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/switch-to-port", methods=["POST"])
@extract_pman_args
def switch_to_port(port):
    current_app.logger.debug(f"Called aurora switch-to-port({port})")
    command_string = f"I{port}R"
    command = format_command(data=command_string) 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/pull", methods=["POST"])
@extract_pman_args
def pull(volume):
    current_app.logger.debug(f"Called aurora pull({volume})")
    steps = vol_to_steps(float(volume))
    command = format_command(f"P{steps}R") 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/push", methods=["POST"])
@extract_pman_args
def push(volume):
    current_app.logger.debug(f"Called aurora push({volume})")
    steps = vol_to_steps(float(volume))
    command = format_command(f"D{steps}R") 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/custom", methods=["POST"])
@extract_pman_args
def custom(s):
    current_app.logger.debug(f"Called aurora custom({s})")
    command = format_command(s) 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}

@aurora_pump.route("/is-busy", methods=["POST"])
@extract_pman_args
def isBusy():
    current_app.logger.debug(f"Called aurora isBusy()")
    status = is_busy()
    if status:
        message = 'pump is busy'
    else:
        message = 'pump is available'
    return {'status':status,'message':message}

@aurora_pump.route("/bubble-bust-transfer", methods=["POST"])
@extract_pman_args
def bubbleBustTransfer(from_port, waste_port, to_port, volume, fraction_air):
    """ 
    Special Transfer designed to eliminate air bubbles through repeated draw and release.
    Here's the core idea: 
        Say a transfer draws some fraction_air
        fraction_air is a function of fluid viscosity, syringe speed, and tubing diameter(s).
        The most efficient way to get rid of this air would be to turn to an output line and push it out
        Then turn back to the input valve and pull more solution.
        Notice that you'll have to pull volume_2 = fraction_air * volume_1
        This means that the volume of air left after the second transfer = fraction_air ** 2 * volume_1
        In general, total_fraction_air(n) = fraction_air ** n,
            where n is number of recursive calls
        To get to some target_fraction,
            target_fraction = fraction_air ** n
            log_fa(target_fraction) = log_fa(fraction_air ** n) = n
            n = log(target_fraction) / log(fraction_air)
    """
    from_port = int(from_port)
    waste_port = int(waste_port)
    to_port = int(to_port)
    volume = float(volume)
    fraction_air = float(fraction_air)
    target_fraction = 0.02
    min_steps = 250 # anything less than this is not worth pulling 
    current_app.logger.debug(f"Called aurora bubbleBustTransfer({from_port, waste_port, to_port, volume, fraction_air})")
    num_loops = round(log(target_fraction) / log(fraction_air))
    current_app.logger.debug(f"Going to do {num_loops} transfers")
    volume_in_steps = vol_to_steps(volume)
    command = ''
    # this loop loads the syringe without air bubbles
    for _ in range(num_loops):
        input_valve = f'I{from_port}'
        pull = f'P{volume_in_steps}'
        output_valve = f'O{waste_port}'
        volume_in_steps = int(fraction_air * volume_in_steps)
        push =  f'D{volume_in_steps}'
        command += input_valve + pull + output_valve + push
        if volume_in_steps <= min_steps:
            break
    # after syringe is full, transfer to the final port
    command += f'O{to_port}A0R'
    command = format_command(command)
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}
