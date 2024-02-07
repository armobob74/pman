from flask import Blueprint, request, current_app
from functools import wraps

pman = Blueprint('pman', __name__,url_prefix='/pman')

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

@pman.route("/example", methods=["POST"])
@extract_pman_args
def transfer(arg1, arg2, arg3):
    message = f"Got args in this format: [{arg1},{arg2},{arg3}]"
    return {'status':'ok','message':message}
