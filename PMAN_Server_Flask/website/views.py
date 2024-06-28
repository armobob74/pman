from flask import Blueprint, current_app, render_template, request, flash, jsonify, redirect, url_for
import pdb
from .pman_blueprints.csv_utils import read_csv
from .scheduler import remove_expired_jobs_and_rewrite_csv
import json

views = Blueprint('views', __name__)

@views.context_processor
def inject_config():
    # allows the chosen pman config to be used by the templates in this blueprint
    # primarily for conditional rendering of sidecards
    return current_app.config['pman-config']

@views.route('/')
def index():
    if 'home_page' in current_app.config['pman-config']:
        homepath = current_app.config['pman-config']['home_page']
        if homepath != '/':
            return redirect(homepath)
    return render_template('index.html')

@views.route('/settings')
def settings():
    return render_template('settings.html')

@views.route('/example')
def example():
    """ Show an example of a typical PMAN form """
    return render_template('example.html')

@views.route('/aurora-valve/switch-to-port')
def auroraValveSwitchToPort():
    """ Switch to desired port on aurora valve """
    return render_template('aurora-valve/switch_to_port.html')

@views.route('/aurora-pump/transfer')
def auroraPumpTransfer():
    return render_template('aurora-pump/transfer.html')

@views.route('/aurora-pump/set-velocity')
def auroraPumpSetVelocity():
    return render_template('aurora-pump/set-velocity.html')

@views.route('/aurora-pump/control')
def auroraPumpControl():
    DEFAULT_SYRINGE_SPEED = 15 # mL/min
    pman_config = current_app.config['pman-config']
    instrument_info = pman_config['instrument_info']
    syr_speed = DEFAULT_SYRINGE_SPEED
    if "settings" in pman_config and "max-syringe-speed" in pman_config['settings']:
        syr_speed = pman_config["settings"]["max-syringe-speed"]
    return render_template('aurora-pump/control.html',syringe_speed=syr_speed, **instrument_info)

@views.route('/aurora-pump/custom')
def auroraPumpCustom():
    return render_template('aurora-pump/custom.html')

@views.route('/aurora-pump/bubble-bust-transfer')
def auroraPumpBubbleBust():
    return render_template('aurora-pump/bubble_bust_transfer.html')

@views.route('/aurora-pump/check-bus-connectivity')
def auroraPumpCheckBusConnectivity():
    pman_config = current_app.config['pman-config']
    instrument_info = pman_config['instrument_info']
    addresses = instrument_info['addresses']
    serial_port = pman_config['serial_port']
    return render_template('aurora-pump/check_bus_connectivity.html', addresses=addresses,serial_port=serial_port)

@views.route('/release-scheduler/release-scheduler')
def releaseScheduler():
    if 'scheduler_tablepath' in current_app.config['pman-config']:
        tablepath = current_app.config['pman-config']['scheduler_tablepath']
        remove_expired_jobs_and_rewrite_csv(tablepath)
        data = read_csv(tablepath)
    else:
        data = [['table','not','loaded'],['please','edit','config']]
    headers = data[0]
    rows = data[1:]
    return render_template('release-scheduler/release-scheduler.html', headers=headers, rows=rows,bad_format_text=current_app.config['bad-format-text'])

@views.route('/release-scheduler/release-schedule')
def releaseSchedule():
    # show the scheduler table.
    job_list = [(job.id, job.next_run_time.strftime('%B %d, %Y at %I:%M %p %Z')) for job in current_app.scheduler.get_jobs()]
    return render_template('release-scheduler/release-schedule.html', job_list=job_list)

@views.route('/kamoer-peri/control')
def kamoerPeriControl():
    pman_config = current_app.config['pman-config']
    instrument_info = pman_config['instrument_info']
    addrs = instrument_info['addrs']
    return render_template('kamoer-peri/control.html',addrs=addrs)
