# Runner
## Table of Contents
<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Intro](#intro)
- [Custom CSVs](#custom-csvs)
- [Persist Modular Automation Network (PMAN) API](#persist-modular-automation-network-pman-api)
   * [Overview](#overview)
   * [PMAN Endpoints](#pman-endpoints)
- [PMAN Runner Config](#pman-runner-config)
- [Flask tips](#flask-pman)
   * [Argument Parsing](#argument-parsing)
   * [Serial Communication](#serial-communication)
   * [Logging](#logging)

<!-- TOC end -->


<!-- TOC --><a name="intro"></a>
## Intro
The primary purpose of the runner is to operate in CSV mode. An example of the universal PMAN csv structure is shown below:
<table>
    <thead>
        <th>Port</th>
        <th>Endpoint</th>
        <th>Arg 1</th>
        <th>Arg 2</th>
        <th>Arg 3</th>
    </thead>
    <tbody>
        <tr>
            <td>5001</td>
            <td>move-to-well</td>
            <td>0</td>
            <td>0</td>
            <td></td>
        </tr>
        <tr>
            <td>5000</td>
            <td>transfer</td>
            <td>0</td>
            <td>5</td>
            <td>0.3</td>
        </tr>
        <tr>
            <td>5001</td>
            <td>move-to-well</td>
            <td>0</td>
            <td>1</td>
            <td></td>
        </tr>
    </tbody>
</table>

This can be transpiled into requests to be sent to the various components connected to the runner. The columns are described as follows:
 - The `Port` column tells the runner what the address of the desired instrument's server is. 
 - The `Endpoint` column tells the runner what endpoint to send its request to
 - The `Arg` columns tell the runner what arguments to include in its request

The first line of the CSV above would be transpiled into something like this:
```javascript
    fetch('http://localhost:5000/pman/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(
                {'args':["0","0"]}
            )
    });
```

<!-- TOC --><a name="custom-csvs"></a>
## Custom CSVs
If desired, runners can define their own custom CSV structures that depend on setup configuration variables. For a setup with an SPM and a SmartStageXY, a custom CSV may look like this:
<table>
    <thead>
        <th>Liquid</th>
        <th>Volume (mL)</th>
        <th>Well_X</th>
        <th>Well_Y</th>
        <th>Speed</th>
    </thead>
    <tbody>
        <tr>
            <td>water</td>
            <td>0.3</td>
            <td>0</td>
            <td>0</td>
            <td>200</td>
        </tr>
        <tr>
            <td>ethanol</td>
            <td>0.3</td>
            <td>0</td>
            <td>1</td>
            <td>150</td>
        </tr>
        <tr>
            <td>Elmer's Glue</td>
            <td>0.3</td>
            <td>0</td>
            <td>2</td>
            <td>20</td>
        </tr>
    </tbody>
</table>

The runner would use its configuration to map that CSV to PMAN API calls, abstracting away much complexity.
<!-- TOC --><a name="persist-modular-automation-network-pman-api"></a>
## Persist Modular Automation Network (PMAN) API
<!-- TOC --><a name="overview"></a>
### Overview
PMAN provides a standardized way for Automation Modules to talk to each other. A PMAN request is a post request with a body component that looks like this:
```json
{
    "args":[
        "arg1",
        "arg2",
        "etc"
    ],
}
```
This structure exists so that it's easy for the front-end to turn a CSV row into an API call.

The standard response looks like this:
```json
{
    "status":"No Error",
    "message":"Have a nice day"
}
```
The `status` field is not for the HTTP status, it's for communicating whether anything is wrong with the instrument.
The `message` field is for any information that the instrument may wish to commuicate to the operator -- things like "initiating transfer from port 0 to port 3". This structure is so that it's easy to display something like this to the user in an embedded terminal:
```
localhost:5000 -- No Error -- initiating transfer from port 0 to port 3
```
<!-- TOC --><a name="pman-endpoints"></a>
### PMAN Endpoints
Most PMAN endpoints will accept a request, start an action, and return a response when the action is complete.

All PMAN endpoints begin with `/pman`. This makes them easy to find and identify.
For a Flask API implementation, it is recommended to put PMAN endpoints in their own Blueprint.
The standard endpoints are:
- `/pman/` -- must respond to a GET request. Used by runner to check to see if a server is running.
- `/pman/hardstop` -- must respond to any type of request. Tells the instrument to immediately stop what it is doing.


<!-- TOC --><a name="pman-runner-config"></a>
## PMAN Runner Config
PMAN runners can make use of configuration files to abstract away technical details of PMAN setups. An example config is shown below:
```json
{
    "instruments": {
        "SmartStageXY": [
            {
                "network-port": 5001
            }
        ],
        "SPM": [
            {
                "network-port": 5000,
                "valve-map": {
                    "1":"air",
                    "2":"dihydrogen monoxide",
                    "12":"waste"
                }
            },
            {
                "network-port": 5003,
                "valve-map": {
                    "1":"air",
                    "2":"Toluene",
                    "12":"waste"
                }
            }
        ]
    }
}
```
This config describes a setup with two SPM pumps and one SmartStageXY. The SPM servers are running on localhost:5000 and localhost:5003, while the SmartStageXY is running on localhost:5001. The SPMs are configured with valve maps to tell the runner where various liquids are.

<!-- TOC --><a name="flask-pman"></a>
## Flask tips
There are many ways to implement a server that can accept PMAN requests. The most popular way right now is to use Python's `Flask` library. Common themes include argument parsing, serial communication, and UI design.
<!-- TOC --><a name="argument-parsing"></a>
### Argument Parsing
For ease of use with spreadsheets, the arguments of PMAN requests are sent in a list. The server must know the order to expect the arguments, and then assign them to variables. It's recommended to use a decorator to simplify this process:
```python
def extract_pman_args(f):
    """
    Extract the pman args from the request and plug them into the decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = json.loads(request.data)
        args = data.get('args',[])
        return f(*args)
    return decorated_function

@pman.route("/transfer", methods=["POST"])
@extract_pman_args
def transfer(from_port, to_port, volume):
    response = app.connection.transfer(from_port, to_port, volume)
    message = parseMachineResponse(response)
    return {'status':'ok','message':message}
```

<!-- TOC --><a name="serial-communication"></a>
### Serial Communication
Serial communication can be handled by the `pyserial` library. Serial communication involves transmitting data between a computer and peripheral devices sequentially, bit by bit. Because there's only one connection, it's advisable to set it as a singleton `app.connection` and manage all requests through this one instance. When designing `app.connection`, be sure to provide an easy way to interrupt the connection and provide a hardstop command to the machine. This should be done as `app.connection.hardstop()`. A good way to do this is to use a `Lock` and an `interrupt_flag`. An example is shown below:
```python
from flask import Flask
import serial
from threading import Lock
class Connection:
    def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=9600):
        """
        Initialize the connection
        """
        self.serial = serial.Serial(serial_port,baud_rate)
        self.interrupt_flag = False
        self.lock = Lock() # for thread safety

    def hardstop(self, hardstop_command='T'):
        """
        enable emergency stop if necessary.
        """
        self.interrupt_flag = True
        response = self.send(self.prepare_command(hardstop_command))
        return response

    def prepare_command(self, data, address='0'):
        """
        Command format: <address><data><CR>
        """
        return f"{address}{data}\r"

    def send(self,command, read_until_char='\n'):
        with self.lock:
            if self.interrupt_flag:
                raise InterruptedError("Operation Interrupted")
            self.serial.send(command.encode())
            response = self.serial.read_until(read_until_char.encode())
        return self.parse_response(response)

    def parse_response(self, response):
        """
        Depends on the machine's response format
        """
        response_data = response.decode().strip()
        return response

    def reset_interrupt(self):
        self.interrupt_flag = False
        

def create_app():
    app = Flask(__app__)
    app.connection = Connection()
app = create_app()
```
<!-- TOC --><a name="logging"></a>
### Logging
Flask uses Python's standard logging system. You are encouraged to check out [logging.md](docs/logging.md) for a quick overview of how that works. Flask's default logger is stored at `app.logger`, and for most purposes it's not necessary to replace it. Here's an example of how you may add custom handlers to this logger:
```python
import logging
import os
from flask import Flask

LOG_DIR = 'logs'
INFO_FILE = 'info.log'
DEBUG_FILE = 'debug.log'

def create_handlers():
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    debug_path = os.path.join(LOG_DIR, DEBUG_FILE)
    info_path = os.path.join(LOG_DIR, INFO_FILE)

    debug_handler = logging.FileHandler(debug_path)
    debug_handler.setLevel(logging.DEBUG)
    info_handler = logging.FileHandler(info_path)
    info_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    debug_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)

    return [debug_handler, info_handler]

def create_app():
    app = Flask(__name__)
    for handler in create_handlers():
        app.logger.addHandler(handler)
    #...[the rest of your app factory here]...#
```
