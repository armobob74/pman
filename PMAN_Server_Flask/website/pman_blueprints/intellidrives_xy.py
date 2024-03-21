from flask import current_app, request, Blueprint
import pdb

intelli_xy = Blueprint('intelli_xy',__name__, url_prefix='/pman/intelli-xy')

def format_command(axis_letter, command_code, command_parameters):
    """ 
    [<.>axis letter] [command code] [command parameters] <CR> 

    Axis letter:
        A for X-axis
        B for Y-axis

    Command code:
        Code    Command     Description
        -------------------------------------------------------------------------------------
        s       Set         Set a value of a parameter in ram or flash.
        -------------------------------------------------------------------------------------
        g       Get         Read the value of a parameter in ram or flash.
        -------------------------------------------------------------------------------------
        c       Copy        Copy the value of a parameter from ram to flash or flash to ram.
        -------------------------------------------------------------------------------------
        r       Reset       Reset the drive.
        -------------------------------------------------------------------------------------
        t       Trajectory  Trajectory generator command.
        -------------------------------------------------------------------------------------
        i       Register    Read or write the value of a CVM program register
        -------------------------------------------------------------------------------------

    Command params:
        list of hex string values

    """
    data = f"{axis_letter} {command_code} {' '.join(command_parameters)}"
    current_app.logger.debug(f"Formatting intelli-xy command data: {data}")
    return f'{data} \r'.encode()

def format_set(axis_letter,memory_bank,param_id,value):
    """
    axis_letter: A or B
    memory_bank: f (flash) or r (RAM)
    parameter_id: id of param to change
    value: the value to set
    """
    # yes the first param is indeed 2 params
    # idk why they designed it that way -- ask the manual
    params = [f'{memory_bank}{param_id}', f'{value}']
    return format_command(axis_letter,'s',params)

def format_get(axis_letter,memory_bank,param_id):
    """
    axis_letter: A or B
    memory_bank: f (flash) or r (RAM)
    parameter_id: id of param to read
    """
    # yes the param is indeed 2 params
    # idk why they designed it that way -- ask the manual
    params = [f'{memory_bank}{param_id}']
    return format_command(axis_letter,'s',params)


def parse_response(response_bytes):
    # TODO
    return 'idk'

@intelli_xy.route("/status", methods=["GET"])
def status():
    # TODO
    status = 'idk'
    return {'status':status,'message':''}
