# PMAN Server

## Overview

This is a general-purpose server designed to make it easy to integrate lab instruments into the Persist Modular Automation Network (PMAN). For each instrument, you'd run one instance of the server. Each instance will be configured differently for each instrument. For example, here's what our aurora valve config looks like:

```json
{
  "port": 5110,
  "serial_port": "/dev/ttyUSB0",
  "sidecards": [["Switch to Port", "/aurora-valve/switch-to-port"]]
}
```

The `port` argument tells the server which port to run on, while the `serial_port` argument tells the server what port to communicate with. The `sidecards` argument controls the rendering of `layout.html`.

To select a config, pass it as an argument to the `main.py` program like so:

```zsh
python config_name.json
```

Note that `config_name` is NOT a full path -- all configs are stored in the `website/configs` directory

## Instrument Blueprints

Each class of instrument gets its own blueprint in `website/pman_blueprints`. This blueprint should handle all logic related to the instrument, including compilation of serial commands. But the serial connection itself is managed by the `app.connection` object.

## Serial Communication

The server comes with an `app.connection` object, which acts as a serial port manager. It has a command queue, but you can also bypass this queue with the `instant=True` argument. The `app.connection` object likes to deal with byte strings, so the logic for setting up those byte strings should be done in your instrument blueprint.

```python3
# this is in website/pman_blueprints/aurora_valve.py
def format_command(cmd, arg1=b'\x00', arg2=b'\x00'):
    start_bytes = b'\xCC\x00'
    end_bytes = b'\xDD'
    cmd_arg1_arg2 = cmd + arg1 + arg2
    checksum = sum(start_bytes + cmd_arg1_arg2 + end_bytes)
    HB = (checksum >> 8) & 0xFF  # Shift right by 8 bits and mask to get HB
    LB = checksum & 0xFF  # Mask to get LB
    final_command = start_bytes + cmd_arg1_arg2 + end_bytes + bytes([LB, HB])
    return final_command

@aurora_valve.route("/switch-to-port", methods=["POST"])
@extract_pman_args
def switch_to_valve(port_number):
    current_app.logger.debug(f"Called switch_to_valve({port_number})")
    to_port = int(port_number).to_bytes(1, "little")
    command = format_command(cmd=b'\x44', arg1=to_port)
    response = current_app.connection.send(command, immediate=True)
    return {'status':'ok','message':response.hex()}
```
