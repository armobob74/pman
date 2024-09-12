#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or use sudo."
  exit 1
fi

read -p "Where is your device now? (e.g., /dev/ttyUSB7) >> " device_path

# Check if the device exists
if [ ! -e "$device_path" ]; then
    echo "Device not found at $device_path. Please check and try again."
    exit 1
fi

device_name=$(basename "$device_path")

read -p "What do you want the symlink name to be? >> " symlink_name

udev_info=$(udevadm info -a -n "$device_path")

idVendor=$(echo "$udev_info" | grep -m 1 'ATTRS{idVendor}' | awk -F'==' '{print $2}' | tr -d '"')
idProduct=$(echo "$udev_info" | grep -m 1 'ATTRS{idProduct}' | awk -F'==' '{print $2}' | tr -d '"')

if [ -z "$idVendor" ] || [ -z "$idProduct" ]; then
    echo "Could not find idVendor or idProduct. Please ensure the device is correctly connected."
    exit 1
fi

echo "Found it! Creating rule now."

rule="SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"$idVendor\", ATTRS{idProduct}==\"$idProduct\", SYMLINK+=\"$symlink_name\", MODE=\"0666\""

echo "$rule" | sudo tee -a /etc/udev/rules.d/99-pman.rules

sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Rule created successfully and placed in /etc/udev/rules.d/99-pman.rules"
