import pdb
from .aurora_pump import transfer_command_string, format_command, parse_response
from .csv_utils  import write_csv
from flask import current_app, request, Blueprint, redirect
from ..scheduler import  reload_scheduler, parser
from datetime import datetime
from dateutil import tz, parser

from tzlocal import get_localzone

release_scheduler = Blueprint('release_scheduler',__name__, url_prefix='/pman/release-scheduler')


# appended to things in table that are bad format
bad_format_text = ' -- BAD FORMAT'

@release_scheduler.route("/save-table", methods=["POST"])
def saveTable():
    """ 
    Save the table as a CSV, and also update the aptscheduler table
    Making an exception and not using PMAN arg formatting for this endpoint.
    """
    scheduler_tablepath = current_app.config['pman-config']['scheduler_tablepath']
    data = request.json['data']
    local_tz = get_localzone()

    for i, row in list(enumerate(data))[1:]:
        t0 = row[-1]
        try:
            parser.parse(t0)
        except parser.ParserError:
            # gotta remove to avoid multiple appends
            t0 = t0.replace(bad_format_text, '')
            # append the warning so user knows it's bad format
            data[i][-1] = t0 + bad_format_text

    message = write_csv(data, scheduler_tablepath, '\t') 
    # removes everything from our internal scheduler and replaces it with the contents of the CSV
    reload_scheduler(current_app.scheduler, scheduler_tablepath)
    if not message == True:
        print(message) # it's an error message
        return "There has been an error"
    return redirect('/')

@release_scheduler.route("/show-schedule", methods=["GET"])
def showSchedule():
    """ 
    return the scheduler job list in text form.
    show the job list directly from the apscheduler, not from the csv backup table
    """
    job_list = current_app.scheduler.get_jobs()
    result = '\n'.join([str(job) for job in job_list])
    return result
