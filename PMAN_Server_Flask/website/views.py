from flask import Blueprint, current_app, render_template, request, flash, jsonify, redirect, url_for
import json

views = Blueprint('views', __name__)

@views.context_processor
def inject_config():
    # allows the chosen pman config to be used by the templates in this blueprint
    # primarily for conditional rendering of sidecards
    return current_app.config['pman-config']

@views.route('/')
def index():
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
    return render_template('aurora-pump/control.html')

@views.route('/aurora-pump/custom')
def auroraPumpCustom():
    return render_template('aurora-pump/custom.html')

@views.route('/aurora-pump/bubble-bust-transfer')
def auroraPumpBubbleBust():
    return render_template('aurora-pump/bubble_bust_transfer.html')
