from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for

views = Blueprint('views', __name__)

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
