from queue import Queue
from threading import Lock, Thread
import serial
from serial.serialutil import SerialException

class MockSerial:
    """This class is used for manual testing when an actual serial connection does not exist"""
    def __init__(self, *args, **kwargs):
        self.read_buffer = bytearray()
        self.write_buffer = bytearray()
        self.is_open = True  # Simulate the port being open initially

    def read(self, size=1):
        data = self.read_buffer[:size]
        self.read_buffer = self.read_buffer[size:]
        return bytes(data)

    def write(self, data):
        self.write_buffer.extend(data)
        return len(data)  # Typically, serial.write returns the number of bytes written

    def read_until(self, terminator=b'\n', size=None):
        result = bytearray()
        while True:
            if size is not None and len(result) >= size:
                break
            if len(self.read_buffer) == 0:
                break
            next_byte = self.read(1)
            result.extend(next_byte)
            if result.endswith(terminator):
                break
        return bytes(result)

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def flush(self):
        self.write_buffer.clear()

    def in_waiting(self):
        return len(self.read_buffer)
    
class Connection:
    def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=9600):
        try:
            self.serial = serial.Serial(serial_port, baud_rate)
        except SerialException:
            print("### Could not open serial port, running in no-serial mode ###")
            self.serial = MockSerial()
        self.interrupt_flag = False
        self.lock = Lock()  # for thread safety
        self.command_queue = Queue()
        self.worker_thread = Thread(target=self.process_commands)
        self.worker_thread.daemon = True  # Daemon thread exits when the main program exits
        self.worker_thread.start()

    def hardstop(self, hardstop_command='T'):
        self.interrupt_flag = True
        response = self.send(hardstop_command, immediate=True)  # Immediate flag to bypass queue in emergency
        return response

    def prepare_command(self, data, address='0'):
        return f"{address}{data}\r"

    def send(self, command, immediate=False):
        if immediate:
            with self.lock:
                return self._send_command(self.prepare_command(command))
        else:
            self.command_queue.put(command)

    def _send_command(self, command, read_until_char='\n'):
        if self.interrupt_flag:
            raise InterruptedError("Operation Interrupted")
        self.serial.write(command.encode())
        response = self.serial.read_until(read_until_char.encode())
        return self.parse_response(response)

    def process_commands(self):
        while True:
            command = self.command_queue.get()  # This will block until a command is available
            with self.lock:
                self._send_command(self.prepare_command(command))
            self.command_queue.task_done()  # Mark the processed task as done

    def parse_response(self, response):
        response_data = response.decode().strip()
        return response_data

    def reset_interrupt(self):
        self.interrupt_flag = False
