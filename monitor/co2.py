# communication with Sensair-S8 CO2 sensor via UART pins

import serial
from time import sleep

comm = serial.Serial('/dev/ttyS0', 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

commands = {
    'read': b'\xfe\x04\x00\x03\x00\x01\xd5\xc5',
    'disable_ABC': b'\xfe\x06\x00\x1f\x00\x00\xac\x03',
    'enable_ABC_start': b'\xfe\x06\x00\x1f'

}

def calculate_crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, 'little')

def read():
    comm.flush()

    comm.write(commands['read'])
    sleep(0.05)
    
    data = comm.read(7)
    sleep(0.05)
    
    return int.from_bytes(data[3:5], byteorder='big')

def disable_ABC():
    comm.flush()
    
    comm.write(commands['disable_ABC'])
    sleep(0.05)

    data = comm.read(8)
    
    return data

def enable_ABC(period_hrs=180):
    comm.flush()
    
    period_hex = int.to_bytes(int(period_hrs), 2, byteorder='big')
    
    msg = commands['enable_ABC_start'] + period_hex
    msg += calculate_crc16(msg)
    
    comm.write(msg)
    sleep(0.05)
    
    data = comm.read(8)
    
    return data