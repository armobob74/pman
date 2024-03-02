import sys
sys.path.append('..')
import pytest
from website.connection import Connection  # Adjust the import based on your project structure

@pytest.fixture
def mock_serial(mocker):
    return mocker.patch('serial.Serial')

@pytest.fixture
def connection(mock_serial):
    return Connection(serial_port="dummy_port", baud_rate=9600)

def test_init(connection, mock_serial):
    mock_serial.assert_called_once_with("dummy_port", 9600)
    assert not connection.interrupt_flag
    assert connection.command_queue.empty()

def test_send_enqueue_command(connection, mocker):
    mocker.patch.object(connection, '_send_command')  # Mock the _send_command to ensure it's not called
    connection.send("CMD")
    assert not connection.command_queue.empty()
    assert connection.command_queue.qsize() == 1
    assert connection.command_queue.get_nowait() == "CMD"

def test_hardstop(connection, mocker):
    mock_send = mocker.patch.object(connection, 'send')
    connection.hardstop("T")
    mock_send.assert_called_once_with("T", immediate=True)
    assert connection.interrupt_flag
