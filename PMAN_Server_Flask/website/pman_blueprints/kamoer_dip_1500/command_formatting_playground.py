import struct
import serial 

ser = serial.Serial('/dev/ttyUSB0', timeout=1)

def float_to_bytes(n):
    br = struct.pack('>f', n)
    return  br[2:]+ br[0:2]

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

def set_rpm(rpm,addr=b'\x01'):
    if rpm > 400.0:
        rpm = 400.0
    elif rpm < 0:
        rpm = 0
    cmd = addr + b'\x10\x40\x01\x00\x02\x04' + float_to_bytes(rpm)
    cmd = cmd + crc_calculation(cmd)
    ser.write(cmd)
    return ser.read_until(b'\xc8')

class ModbusFunctions:
        write_single_coil=b'\x05'
        write_multiple_registers=b'\x10'
        read_coils=b'\x01'
        read_discrete_inputs=b'\x02'
        read_holding_registers=b'\x03'
        read_input_registers=b'\x04'

def modbus_write(modbus_function, start_addr, num_registers,num_bytes_to_write,bytes_to_write,addr=b'\x01'):
    """ General purpose function used for modbus commands """
    cmd = addr + modbus_function + start_addr + num_registers + num_bytes_to_write + bytes_to_write
    cmd = cmd + crc_calculation(cmd)
    ser.write(cmd)
    return ser.read_until(b'\xc8')

def motor_start(addr=b'\x01'):
    modbus_function = ModbusFunctions.write_single_coil
    start_addr = b'\x00\x01'
    data = b'\xff\x00'  # Typical data for setting a coil ON
    cmd = addr + modbus_function + start_addr + data
    cmd += crc_calculation(cmd)
    ser.write(cmd)
    return ser.read_until(b'\xc8')

def motor_stop(addr=b'\x01'):
    return modbus_write(
        modbus_function=ModbusFunctions.write_single_coil,
        start_addr=b'\x00\x01',
        num_registers=b'',  # Not needed for writing single coil
        num_bytes_to_write=b'',  # Not needed for writing single coil
        bytes_to_write=b'\x00\x00',
        addr=addr
    )

def uint23_to_bytes(n):
    """return 4 byte representation of unsigned integer"""
    n = int(n)
    rep = n.to_bytes(4, 'big')
    LB = rep[0:2]
    HB = rep[2:] 
    return HB + LB

    

def set_runtime(time_ms, addr=b'\x01'):
    return modbus_write(
        modbus_function=ModbusFunctions.write_multiple_registers,
        start_addr=b'\x40\x05',
        num_registers=b'\x00\x02',
        num_bytes_to_write=b'\x04',  # Not needed for writing single coil
        bytes_to_write=uint23_to_bytes(time_ms),
        addr=addr
    )

set_runtime_cmd = b'\x01\x10\x40\x05\x00\x02\x04\x27\x10\x00\x00\x09\x22'
