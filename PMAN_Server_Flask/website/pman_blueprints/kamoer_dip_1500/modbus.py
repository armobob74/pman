import struct
import serial 

response_len = 8 # we are assuming it's constant but who knows

def float_to_bytes(n):
    br = struct.pack('>f', n)
    return  br[2:]+ br[0:2]

def bytes_to_float(b):
    reverb = b[2:] + b[:2]
    return struct.unpack('>f', reverb)[0]

def crc_calculation(buf,lenl=None):
    if lenl == None:
        lenl = len(buf)
    i=0
    crc_date=0xffff
    while i<lenl:
        crc_date=crc_date^buf[i]
        j=0
        while j<8:
            if crc_date&0x0001:
                crc_date=crc_date>>1
                crc_date=crc_date^0xa001
            else:
                crc_date=crc_date>>1
            j += 1
        i+= 1
    LB = crc_date & 0x00ff
    HB = (crc_date >> 8) & 0x00ff
    return bytes([LB, HB])

class ModbusFunctions:
        read_coils = b'\x01'
        read_discrete_inputs = b'\x02'
        read_holding_registers = b'\x03'
        read_input_registers = b'\x04'
        write_single_coil = b'\x05'
        write_single_register = b'\x06'
        write_multiple_coils = b'\x0F'
        write_multiple_registers = b'\x10'

def uint23_to_bytes(n):
    """return 4 byte representation of unsigned integer"""
    n = int(n)
    rep = n.to_bytes(4, 'big')
    LB = rep[0:2]
    HB = rep[2:] 
    return HB + LB

def extract_data_hr(byte):
    return bytes_to_float(byte[3:7])

def extract_data_cl(byte):
    return byte[3]

class ModbusRTU:
    """ Class that operates modbus over a serial connection """
    def __init__(self, ser: serial.Serial):
        self.ser = ser 

    def modbus_write(self, modbus_function, start_addr, num_registers,num_bytes_to_write,bytes_to_write,addr=b'\x01'):
        """ General purpose function used for modbus commands """
        cmd = addr + modbus_function + start_addr + num_registers + num_bytes_to_write + bytes_to_write
        cmd = cmd + crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(response_len)

    def motor_start(self,addr=b'\x01'):
        modbus_function = ModbusFunctions.write_single_coil
        start_addr = b'\x00\x01'
        data = b'\xff\x00'  # Typical data for setting a coil ON
        cmd = addr + modbus_function + start_addr + data
        cmd += crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(response_len)

    def motor_stop(self,addr=b'\x01'):
        return self.modbus_write(
            modbus_function=ModbusFunctions.write_single_coil,
            start_addr=b'\x00\x01',
            num_registers=b'',  # Not needed for writing single coil
            num_bytes_to_write=b'',  # Not needed for writing single coil
            bytes_to_write=b'\x00\x00',
            addr=addr
        )

    def motor_clockwise(self,addr=b'\x01'):
        return self.modbus_write(
            modbus_function=ModbusFunctions.write_single_coil,
            start_addr=b'\x00\x02',
            num_registers=b'',  # Not needed for writing single coil
            num_bytes_to_write=b'',  # Not needed for writing single coil
            bytes_to_write=b'\xFF\x00',
            addr=addr
        )
    def motor_counterclockwise(self,addr=b'\x01'):
        return self.modbus_write(
            modbus_function=ModbusFunctions.write_single_coil,
            start_addr=b'\x00\x02',
            num_registers=b'',  # Not needed for writing single coil
            num_bytes_to_write=b'',  # Not needed for writing single coil
            bytes_to_write=b'\x00\x00',
            addr=addr
        )

    def set_rpm(self,rpm,addr=b'\x01'):
        #here set motor to clockwise rotation then.
        if rpm < 0: 
            rpm = 0
        elif rpm > 400.0:
            rpm = 400.0
        
        cmd = addr + b'\x10\x40\x01\x00\x02\x04' + float_to_bytes(rpm)
        cmd = cmd + crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(response_len)

    def set_runtime(self,time_ms, addr=b'\x01'):
        return self.modbus_write(
            modbus_function=ModbusFunctions.write_multiple_registers,
            start_addr=b'\x40\x05',
            num_registers=b'\x00\x02',
            num_bytes_to_write=b'\x04',  # Not needed for writing single coil
            bytes_to_write=uint23_to_bytes(time_ms),
            addr=addr
        )

    def change_to_timemode(self,addr=b'\x01'):
        return self.modbus_write(
            modbus_function=ModbusFunctions.write_single_coil,
            start_addr=b'\x00\x04', #address of operation mode
            num_registers=b'',  # Not needed for writing single coil
            num_bytes_to_write=b'',  # Not needed for writing single coil
            bytes_to_write=b'\x00\x00',
            addr=addr
        )

    def change_to_volumemode(self,addr=b'\x01'):
        return self.modbus_write(
            modbus_function=ModbusFunctions.write_single_coil,
            start_addr=b'\x00\x04', #address of operation mode
            num_registers=b'',  # Not needed for writing single coil
            num_bytes_to_write=b'',  # Not needed for writing single coil
            bytes_to_write=b'\xFF\x00',
            addr=addr
        )

    def read_motor_status(self,addr=b'\x01'):
        modbus_function = ModbusFunctions.read_coils
        start_addr = b'\x00\x01'  # Address of the coil register one
        num_registers = b'\x00\x01'  # Number of registers to read (just one coil)
        cmd = addr + modbus_function + start_addr + num_registers
        cmd += crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(6)

    def read_dir(self,addr=b'\x01'):
        modbus_function = ModbusFunctions.read_coils
        start_addr = b'\x00\x02'  # Address of the coil register one
        num_registers = b'\x00\x01'  # Number of registers to read (just one coil)
        cmd = addr + modbus_function + start_addr + num_registers
        cmd += crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(6)

    def read_rpm(self,addr=b'\x01'):
        modbus_function = ModbusFunctions.read_holding_registers
        start_addr = b'\x40\x01'  
        num_registers = b'\x00\x02'  
        cmd = addr + modbus_function + start_addr + num_registers
        cmd += crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(9)

    def read_time(self,addr=b'\x01'):
        modbus_function = ModbusFunctions.read_holding_registers
        start_addr = b'\x40\x05'  
        num_registers = b'\x00\x02'  
        cmd = addr + modbus_function + start_addr + num_registers
        cmd += crc_calculation(cmd)
        self.ser.write(cmd)
        return self.ser.read(9)

set_runtime_cmd = b'\x01\x10\x40\x05\x00\x02\x04\x27\x10\x00\x00'+uint23_to_bytes(0)
