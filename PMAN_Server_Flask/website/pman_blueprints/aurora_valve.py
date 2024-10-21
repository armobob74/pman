from flask import current_app, request, Blueprint
from .utils import extract_pman_args

RESPOSE_LEN = 8 # number of response bytes expected

aurora_valve = Blueprint('aurora_valve',__name__, url_prefix='/pman/aurora-valve')

def cksum(b):
    summation = sum(b)
    HB = (summation >> 8) & 0xFF  # Shift right by 8 bits and mask to get HB
    LB = summation & 0xFF  # Mask to get LB
    return bytes([LB, HB])

def get_change_addr_cmd(old, new):
    cmd = b'\xCC' + old + b'\x00\xFF\xEE\xBB\xAA' + new + b'\x00\x00\x00\xDD'
    cmd = cmd + cksum(cmd)
    return cmd

def get_switch_port_cmd(addr, port):
    addr = int(addr).to_bytes(1,'little')
    port = int(port).to_bytes(1,'little')
    cmd = b'\xCC' + addr + b'\x44' + port + b'\x00\xDD'
    cmd = cmd  + cksum(cmd)
    return cmd

def format_command(cmd, addr=b'\x00', arg1=b'\x00', arg2=b'\x00'):
    start_bytes = b'\xCC' + addr
    end_bytes = b'\xDD'
    cmd_arg1_arg2 = cmd + arg1 + arg2 + end_bytes
    cksum_bytes = cksum(cmd_arg1_arg2)
    final_command = start_bytes + cmd_arg1_arg2 + end_bytes + cksum_bytes
    return final_command

@aurora_valve.route("/switch-to-port", methods=["POST"])
@extract_pman_args
def switch_to_valve(addr, port_number):
    current_app.logger.debug(f"Called switch_to_valve({addr}, {port_number})")
    command = get_switch_port_cmd(addr, port_number)
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':response.hex()}

@aurora_valve.route("/change-addr", methods=["POST"])
@extract_pman_args
def change_addr_api(old_addr, new_addr):
    current_app.logger.debug(f"Changing addr from {old_addr} to {new_addr}")
    old_addr = int(old_addr).to_bytes(1, "little")
    new_addr = int(new_addr).to_bytes(1, "little")
    command = get_change_addr_cmd(old_addr, new_addr)
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':response.hex()}
