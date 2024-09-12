# Bus Scripts
Most of our busses connect to a USB port. On Linux, this will be called something like `/dev/ttyUSB0`. On Windows, it'll be something like COM3.
The problem is that both of these operating systems will change the name of their ports in ways that aren't always easy to follow. Historically, we've always just manually identified our COM ports, but as our systems have gotten more complex and the cost of failure has gotten too high, we're forced to explore ways to automate this task.

## Why it's not trivial
If each serial port spoke to exactly one device, and that device had a unique ID, this task would be easy as cake! Unfortunately, that's not the case. Many of our ports will connect to **RS485 busses**, which can have **up to 16** devices, each with unique addresses! But the device addresses are only unique for the bus, not universally.

## What can be done
First, the type of devices on the bus must be identified. If we set a rule that **each bus must have a device with the address 1**, the bus tester can try a number of communication methods until it finds one that works. Once it finds one that works, it can begin to check which addresses are on the bus. It can then build a **unique bus id** by concatenating the addresses. This unique bus id can be used to find the appropriate pman config file through a lookup table.
