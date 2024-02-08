from flask import current_app, request, Blueprint
from .utils import extract_pman_args

RESPOSE_LEN = 8 # number of response bytes expected

aurora_valve = Blueprint('aurora_valve',__name__, url_prefix='/pman/aurora-valve')

def format_command(cmd, arg1=b'\x00', arg2=b'\x00'):
    start_bytes = b'\xCC\x00'
    end_bytes = b'\xDD'
    cmd_arg1_arg2 = cmd + arg1 + arg2 
    checksum = sum(start_bytes + cmd_arg1_arg2 + end_bytes)
    HB = (checksum >> 8) & 0xFF  # Shift right by 8 bits and mask to get HB
    LB = checksum & 0xFF  # Mask to get LB
    final_command = start_bytes + cmd_arg1_arg2 + end_bytes + bytes([LB, HB])
    return final_command


@aurora_valve.route("/switch-to-port", methods=["POST"])
@extract_pman_args
def switch_to_valve(port_number):
    current_app.logger.debug(f"Called switch_to_valve({port_number})")
    to_port = int(port_number).to_bytes(1, "little")
    command = format_command(cmd=b'\x44', arg1=to_port) 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':response.hex()}

