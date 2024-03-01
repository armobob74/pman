"""
Right now, this scheduler is pretty purpose-built for release testing 
However, it can be expanded to be used by other processes if necessary
"""
import pdb
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime 
from .pman_blueprints.csv_utils import read_csv, write_csv
from dateutil import parser # handles datetime parsing automatically, including with timzones
from uuid import uuid4

def init_scheduler(app):
    """Initialize the scheduler with jobs defined in a CSV file."""
    pman_config = app.config['pman-config']
    if not 'scheduler_tablepath' in pman_config:
        print("### No scheduler_tablepath found in config, running without scheduler ###")
        return
    scheduler = BackgroundScheduler(daemon=True)
    try:
        filepath = pman_config['scheduler_tablepath']
    except KeyError:
        raise KeyError('scheduler_tablepath not found in pman config. Ensure that init_scheduler(app) is placed after the declaration of scheduler_tablepath.')
    try:
        joblist = build_joblist_from_csv(filepath)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file at {filepath}. Error: {e}")

    for net_port, valve_port, dt in joblist:
        add_job_to_scheduler(scheduler, net_port, valve_port, dt)

    app.scheduler = scheduler  # Store the scheduler in the app for future access
    scheduler.start()

def add_job_to_scheduler(scheduler, net_port, valve_port, dt):
    s = f"{net_port}_{valve_port}"
    job = lambda s=s: print(s) 
    job_id = str(uuid4())  # id avoids scheduler collisions if two jobs share a run date
    scheduler.add_job(job, run_date=dt, id=job_id)

def reload_scheduler(scheduler, filepath):
    """Reload the scheduler with jobs from a specified CSV file."""
    scheduler.remove_all_jobs()
    joblist = build_joblist_from_csv(filepath)
    for net_port, valve_port, dt in joblist:
        add_job_to_scheduler(scheduler, net_port, valve_port, dt)

def build_joblist_from_csv(filepath, delimiter='\t'):
    """
    return list of (action, datetime)
    input row format:
    ["5003", "4", "1,2,3","February 23, 2024 at 3:49:10 PM PST"]

    also delete any expired jobs and re-write CSV if necessary
    """
    table = read_csv(filepath, delimiter)
    headers = table[0]
    rows = table[1:]
    joblist = []
    non_expired_rows = []
    for row in rows:
        net_port = row[0]
        valve_port = row[1]
        hours = [float(s) for s in row[2].split(",")]
        dt = parser.parse(row[3])
        row_jobtimes = []
        now = datetime.now(dt.tzinfo)
        for hour in hours:
            delta = timedelta(hours=hour)
            jobtime = dt + delta
            if jobtime > now:
                row_jobtimes.append(jobtime)
                joblist.append((net_port, valve_port, jobtime))
        if len(row_jobtimes) > 0:
            non_expired_rows.append(row)
        num_expired_rows = len(rows) - len(non_expired_rows)
        if num_expired_rows > 0:
            print(f"### found {num_expired_rows} expired rows -- deleting them now ###")
            data = [headers] + non_expired_rows
            write_csv(data, filepath, delimiter)
        else:
            print(f"### found {0} expired rows ###")
    return joblist
