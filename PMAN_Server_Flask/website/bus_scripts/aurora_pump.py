import serial
import os 

import serial.tools.list_ports

potential_addrs = '123456789:;<=>?@'

class AuroraPumpBusIdentifier:
    def __init__(self,port,baud=9600,timeout=0.2):
        self.serial = serial.Serial(port,baud,timeout=timeout)

    def query_addr(self,addr):
        command = f'/{addr}Q\r'.encode()
        self.serial.write(command)
        response = self.serial.read_until(b'\n')
        if len(response) > 0 and response.startswith(b'\xff/0'):
            return True
        return False

    def identify_bus(self):
        """
        Assumptions:
            bus consists only of Aurora pumps or devices with the same communications protocols
            devices each have unique addresses
        Buss ID will be assigned based on the sorted concatenation of the connected addresses
        """
        print(f"Beginning bus identification for port {self.serial.port}")
        bus_id = ''
        for c in potential_addrs:
            is_valid = self.query_addr(c)
            print(f'{c}\t{is_valid}')
            if is_valid:
                bus_id = bus_id + c
        print(f"Done!\nBus ID is: {bus_id}")
        return bus_id

    def close(self):
        self.serial.close()

if __name__ == "__main__":
    import json
    output_file = './aurora_portmap.json'
    ports = [port.device for port in serial.tools.list_ports.comports()]
    port_id_dict = {}
    for p in ports:
        ider = AuroraPumpBusIdentifier(p,timeout=0.2)
        bus_id = ider.identify_bus()
        if len(bus_id) > 0:
            port_id_dict[p] = bus_id
        else:
            print("No Aurora Pumps on this port")
    print(f"Writing to {output_file}")
    print(port_id_dict)
    with open(output_file, 'w') as f:
        json.dump(port_id_dict, f, indent=4)
