from flask import current_app, request, Blueprint
from .utils import extract_pman_args

RESPOSE_LEN = 8 # number of response bytes expected

aurora_valve = Blueprint('aurora_valve',__name__, url_prefix='/pman/aurora-valve')

def check_status_bit(status_bit: int):
    status_dict = {
        0x00: "Normal state: The motor is operating normally.",
        0x01: "Frame error: Communication error occurred due to an incorrect frame format.",
        0x02: "Parameter error: Received parameters are not within the allowed range.",
        0x03: "Optocoupler error: An issue with the optocoupler detection has occurred.",
        0x04: "Motor busy: The motor is currently executing another task.",
        0x05: "Motor stalled: The motor has stopped due to encountering an obstruction or overload.",
        0x06: "Unknown position: The motor cannot identify the current position.",
        0xFE: "Task is being executed: The received command is currently being processed.",
        0xFF: "Unknown error: An unidentified error has occurred."
    }
    return status_dict.get(status_bit, f"Invalid or unknown status bit {status_bit}.")



def cksum(b):
    summation = sum(b)
    HB = (summation >> 8) & 0xFF  # Shift right by 8 bits and mask to get HB
    LB = summation & 0xFF  # Mask to get LB
    return bytes([LB, HB])

def parse_response(response_bytes):
    """
    Parses an 8-byte response message and returns a dictionary with the extracted data and status.
    
    Parameters:
    - response_bytes (bytes): The response message received over serial communication.
    
    Returns:
    - dict: A dictionary containing 'data' and 'status'.
    """
    try:
        if len(response_bytes) != 8:
            return {'data': None, 'status': "Invalid response length"}

        start_code = response_bytes[0]
        address_code = response_bytes[1]
        status_code = response_bytes[2]
        data = response_bytes[3:5]
        end_code = response_bytes[5]

        if start_code != 0xCC or end_code != 0xDD:
            return {'data': None, 'status': "Invalid start or end code"}

        status_message = check_status_bit(status_code)
        return {'message': data.hex(), 'status': status_message}
    except Exception as e:
        return {'message':f"{e}", 'status':'Server Error'}


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
    return parse_response(response)

@aurora_valve.route("/change-addr", methods=["POST"])
@extract_pman_args
def change_addr_api(old_addr, new_addr):
    current_app.logger.debug(f"Changing addr from {old_addr} to {new_addr}")
    old_addr = int(old_addr).to_bytes(1, "little")
    new_addr = int(new_addr).to_bytes(1, "little")
    command = get_change_addr_cmd(old_addr, new_addr)
    response = current_app.connection.send(command, immediate=True)
    return parse_response(response)

@aurora_valve.get("/is-busy/<int:addr>")
def isBusy(addr: int):
    base_command = bytes([0xCC, int(addr), 0x4A, 0x00, 0x00, 0xDD])
    command = base_command + cksum(base_command)
    response = current_app.connection.send(command, immediate=True)
    parsed_response = parse_response(response)
    if parsed_response['status'] == "Motor busy: The motor is currently executing another task.":
        return {'is-busy':True}
    else:
        return {'is-busy':False}
