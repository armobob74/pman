# PMAN

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Intro](#intro)
- [Custom CSVs](#custom-csvs)
- [Persist Modular Automation Network (PMAN) API](#persist-modular-automation-network-pman-api)
  - [Overview](#overview)
  - [PMAN Endpoints](#pman-endpoints)
- [PMAN Runner Config](#pman-runner-config)
- [Server](#flask-pman)
  - [Argument Parsing](#argument-parsing)
  - [Serial Communication](#serial-communication)
  - [Logging](#logging)
- FLIP(#FLIP)

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
fetch("http://localhost:5000/pman/move", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ args: ["0", "0"] }),
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
  "args": ["arg1", "arg2", "etc"]
}
```

This structure exists so that it's easy for the front-end to turn a CSV row into an API call. Sometimes, it's not sufficient though. For example if a user wishes to include optional arguments, list-based parsing falls apart. Fortunately, pman supports an optional `kwargs` parameter for situations like that.

```json
{
  "args": ["arg1", "arg2", "etc"],
  "kwargs": {
    "address": "A",
    "speed": 120
  }
}
```

The standard response looks like this:

```json
{
  "status": "No Error",
  "message": "Have a nice day"
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
- `/pman/status` -- must respond to a GET request. Reports instrument status.
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
          "1": "air",
          "2": "dihydrogen monoxide",
          "12": "waste"
        }
      },
      {
        "network-port": 5003,
        "valve-map": {
          "1": "air",
          "2": "Toluene",
          "12": "waste"
        }
      }
    ]
  }
}
```

This config describes a setup with two SPM pumps and one SmartStageXY. The SPM servers are running on localhost:5000 and localhost:5003, while the SmartStageXY is running on localhost:5001. The SPMs are configured with valve maps to tell the runner where various liquids are.

<!-- TOC --><a name="flask-pman"></a>

## Server

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

Serial communication can be handled by the `pyserial` library. Serial communication involves transmitting data between a computer and peripheral devices sequentially, bit by bit. Because there's only one connection, it's advisable to set it as a singleton `app.connection` and manage all requests through this one instance. When designing `app.connection`, be sure to provide an easy way to interrupt the connection and provide a hardstop command to the machine. This should be done as `app.connection.hardstop()`. A good way to do this is to use a `Lock` and an `interrupt_flag`. We also implement a queue to guarantee that commands are processed in the order that they are sent. An example is shown below:

```python
from flask import Flask
from queue import Queue
from threading import Lock, Thread
import serial

class Connection:
    def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=9600):
        self.serial = serial.Serial(serial_port, baud_rate)
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
    app.logger.setLevel(logging.DEBUG) # so that your debug things are actually shown
    for handler in create_handlers():
        app.logger.addHandler(handler)
    #...[the rest of your app factory here]...#
```

You can use this in your `PMAN` blueprint like so:

```python
# ... rest of import section ... #
from flask import current_app
# ... rest of blueprint code ... #
@pman.route('/some-endpoint',methods=["POST"])
@extract_pman_args
def myFunc(arg1, arg2):
    current_app.debug("Recieved POST request at '/pman/some-endpoint'")
    try:
        do_something(arg1, arg2)
        message = "Performed action successfully"
        status = 'ok'
        current_app.logger.info(message)
    except Exception as e:
        message = f"Failed to perform action: {str(e)}"
        status = 'error'
        current_app.logger.error(message)
    return {'status':status, 'message':message}
```

<!-- TOC --><a name="FLIP"></a>

## FLIP

FLexible Interchange of Processes (FLIP) is a standard format for exchanging processes that are made of PMAN commands. For example, a nice, user-friendly Svelte frontend with interactive features can be used to create a FLIP process, then send it to an always-on Flask server that uses APScheduler capabilities to schedule a runtime for the whole process.

FLIP processes are simple JSON representations that can be run without complex parsing. Here's how one looks inside:

```json
{
  "type": "series",
  "steps": [
    {
      "type": "parallel",
      "steps": [
        {
          "type": "pman",
          "args": [2, 10, 0.5],
          "url": "192.168.68.85:5001/pman/transfer"
        },
        {
          "type": "pman",
          "args": [4, 10, 0.5],
          "url": "192.168.68.85:5003/pman/transfer"
        },
        {
          "type": "series",
          "steps": [
            {
              "type": "pman",
              "args": [1, 2, 0.5],
              "kwargs": { "address": "A" },
              "url": "192.168.68.85:5004/pman/transfer"
            },
            {
              "type": "pman",
              "args": [1, 2, 0.5],
              "kwargs": { "address": "B" },
              "url": "192.168.68.85:5004/pman/transfer"
            }
          ]
        }
      ]
    },
    {
      "type": "post",
      "url": "my-notebook-website.com/takenote",
      body = {"put your request body":"here"}
    }
  ]
}
```
Here's what to notice about the process above:
- FLIP processes can contain series of steps, including parallel and sequential steps.
- The example FLIP process includes PMAN commands with specific arguments and URLs for transfer.
- You can also send normal POST requests, which may be useful for non-PMAN needs.
- Types are always lowercase

Below is a table of all possible "type" values and a short explanation of what they do:

| Type    | Description                                                         |
|---------|---------------------------------------------------------------------|
| series  | Executes "steps" in a series, one after the other                   |
| parallel| Executes "steps" in parallel, all at the same time                  |
| pman    | Executes a PMAN command with specified "args" and optional "kwargs" |
| post    | Sends a normal POST request with a specified "body"                 |
