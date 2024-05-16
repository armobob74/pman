from typing import Union
import struct
import serial 
import pdb

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

cmd = b'\x01\x10\x40\x01\x00\x02\x04\x00\x00\x42\x48'
cmd = cmd + crc_calculation(cmd)
