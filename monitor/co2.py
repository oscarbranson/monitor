# communication with Sensair-S8 CO2 sensor via UART pins

import serial
from time import sleep
from pathlib import Path

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

class SensorError(Exception):
    def __init__(self, message="Can't communicate with sensor"):
        self.mssage = message
        super().__init__(self.message)

class Sensor:
    def __init__(self, port='/dev/ttyS0'):
        self.port = port
        self.comm = None
        
        self.open()
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        return False
    
    def open(self):
        if not self.comm:
            self.comm = serial.Serial(self.port, 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
            self.ABC_on = False
                
    def close(self):
        if self.comm and self.comm.is_open:
            self.comm.close()
            self.comm = None
    
    def read(self):
        self.comm.flushInput()
        
        self.comm.write(commands['read'])
        sleep(0.05)
        
        if self.comm.in_waiting > 0:
            data = self.comm.read(7)
            sleep(0.05)
            value = int.from_bytes(data[3:5], byteorder='big')
        else:
            raise SensorError('No response from CO2 sensor. Is it connected?')
        
        self.comm.flushOutput()

        return value
    
    def disable_ABC(self):
        self.comm.flushInput()
        
        self.comm.write(commands['disable_ABC'])
        sleep(0.05)
        
        data = self.comm.read(8)
        
        self.ABC_on = not (data == commands['disable_ABC'])
        
        self.comm.flushOutput()

    
    def enable_ABC(self, period_hrs=180):
        self.comm.flushInput()
        
        period_hex = int.to_bytes(int(period_hrs), 2, byteorder='big')
        
        msg = commands['enable_ABC_start'] + period_hex
        msg += calculate_crc16(msg)
        
        self.comm.write(msg)
        sleep(0.05)
        
        data = self.comm.read(8)
        
        self.ABC_on = data == msg
        
        self.comm.flushOutput()

    
    def close(self):
        self.comm.close()