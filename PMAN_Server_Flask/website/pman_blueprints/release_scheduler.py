from .aurora_pump import transfer_command_string, format_command, parse_response
from .utils import extract_pman_args
from flask import current_app, request, Blueprint
from ..scheduler import add_job_to_scheduler

release_scheduler = Blueprint('release_scheduler',__name__, url_prefix='/pman/release-scheduler')

@release_scheduler.route("/transfer", methods=["POST"])
@extract_pman_args
def add_job(jobs):
    """
    jobs: a list of (job, datetime)
    """
    current_app.logger.debug(f"Called release scheduler add_job({jobs})")
    volume = float(volume)
    command_string = transfer_command_string(from_port, to_port, volume)
    command = format_command(data=command_string) 
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':parse_response(response)}
