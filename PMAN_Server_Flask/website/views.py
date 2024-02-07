from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('index.html')
