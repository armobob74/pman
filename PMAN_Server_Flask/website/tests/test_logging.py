import os, sys
import pdb
import pytest
sys.path.append('..')
sys.path.append('../..')
from website import create_app, LOG_DIR, INFO_FILE, DEBUG_FILE

@pytest.fixture
def app():
    os.chdir('../..')
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture
def debug_log_file():
    debug_path = os.path.join(LOG_DIR, DEBUG_FILE)
    with open(debug_path, 'w'):  # Clear the log file before the test
        pass
    yield debug_path

@pytest.fixture
def info_log_file():
    info_path = os.path.join(LOG_DIR, INFO_FILE)
    with open(info_path, 'w'):  # Clear the log file before the test
        pass
    yield info_path

def test_log_files_exist(debug_log_file, info_log_file):
    assert os.path.exists(debug_log_file)
    assert os.path.exists(info_log_file)

def test_logger_level(app):
    assert app.logger.getEffectiveLevel() == logging.DEBUG

def test_debug_logging(app, debug_log_file):
    test_message = "This is a debug message"
    app.logger.debug(test_message)
    with open(debug_log_file) as f:
        logs = f.read()
    assert test_message in logs

def test_info_logging(app, info_log_file):
    test_message = "This is an info message"
    app.logger.info(test_message)
    with open(info_log_file) as f:
        logs = f.read()
    assert test_message in logs

