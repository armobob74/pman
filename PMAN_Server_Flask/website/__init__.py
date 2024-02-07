from flask import Flask
import sass
from .views import views

def create_app():
    sass.compile(dirname=('./website/static/sass','./website/static/css'))
    app = Flask(__name__)
    app.register_blueprint(views, url_prefix='/')
    return app
