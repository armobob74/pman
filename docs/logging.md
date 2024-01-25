# Understanding Python's Logging System

Python's logging system provides a flexible framework for emitting log messages from Python programs. Loggers are the entry point into the logging system. They take in log messages and then pass them on to the handlers.

## How Python Logging Works

1. **Logging a Message**: 
   When a log message is created in the code (e.g., `logger.info("Your log message")`), it is sent to the logger object.

2. **Log Level Check**: 
   The logger checks the log message's level (such as DEBUG, INFO, WARNING, etc.) against its configured level. If the message's level is lower than the logger's level, the logger ignores it. If it's the same or higher, the logger processes the message.

3. **Handler Dispatch**: 
   The logger forwards the message to all attached handlers. A logger can have multiple handlers, each potentially with different configurations.

4. **Handler Processing**: 
   Each handler, upon receiving a log message, checks if the message's level meets its threshold. If so, the handler formats the message according to its configuration and outputs it to its destination, which could be the console, a file, an email server, a web service, etc.

5. **Formatting with Formatter**: 
   Handlers often use a formatter to define the final layout of the log message, which can include elements like timestamps, logger names, and more.


This system allows for significant flexibility. For instance, it's possible to have:

- Multiple loggers with different levels of verbosity.
- Each logger can have multiple handlers, which can perform different actions with the same log messages.
- One handler might write ERROR messages to a file for later analysis.
- Another handler could send INFO messages to the console for real-time monitoring.

## Code example

```python
import logging
import os

# the logger recieves messages
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set logger to handle DEBUG and higher level logs

# handlers determine what to do with the messages
# this one logs everything to the debug log
debug_handler = logging.FileHandler('logs/debug.log')
debug_handler.setLevel(logging.DEBUG)  # This handler takes care of DEBUG messages

# this one logs only info and above to the info log 
info_handler = logging.FileHandler('logs/info.log')
info_handler.setLevel(logging.INFO)  # This handler takes care of INFO messages

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)

logger.addHandler(debug_handler)
logger.addHandler(info_handler)

if not os.path.exists('logs'):
    os.mkdir('logs')

# Here are some usage examples:
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```
