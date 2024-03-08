from flask import Blueprint, request, current_app
from functools import wraps
import json

busy_chars = '@ABCDFGIJKO'
ready_chars='`abcdfgijko'

def extract_pman_args(f):
    """
    Extract the pman args from the request and plug them into the decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = json.loads(request.data)
        args = data.get('args',[])
        return f(*args)
    return decorated_function

def statusParserHamiltonAurora(statusChar):
    """
    Parse the status char in hamilton and aurora pumps 
    This assumes that the Aurora uses the same status chars as Hamilton -- definitely double check that
    """
    if statusChar in busy_chars:
        readiness = 'Busy'
    elif statusChar in ready_chars:
        readiness = 'Ready'
    else:
        return 'Unknown'

    if statusChar == '@':
        key = '`'
    else:
        key = statusChar.lower()
    status_dict = {
            '`':'No error',
            'a':'Initialization error',
            'b':'Invalid command',
            'c':'Invalid operand',
            'd':'Invalid command sequence',
            'f':'EEPROM failure',
            'g':'Syringe not initialized',
            'i':'Syringe overload',
            'j':'Valve overload',
            'k':'Syringe move not allowed',
            'o':'Pump is busy executing commands in the command buffer.'
    }
    status = f"{readiness}, {status_dict[key]}"
    return status



