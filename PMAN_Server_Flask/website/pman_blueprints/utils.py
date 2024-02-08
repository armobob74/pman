from flask import Blueprint, request, current_app
from functools import wraps
import json

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
