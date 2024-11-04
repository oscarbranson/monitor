# communication with Sensair-S8 CO2 sensor via UART pins

import serial
from time import sleep
from pathlib import Path

commands = {
    'read': b'\xfe\x04\x00\x03\x00\x01\xd5\xc5',
    'ABC_disable': b'\xfe\x06\x00\x1f\x00\x00\xac\x03',
    'ABC_enable_start': b'\xfe\x06\x00\x1f',
    'ABC_get_period': b'\xfe\x03\x00\x1f\x00\x01\xa1\xc3'
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
        
        self.connect()
            
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        return False
    
    def connect(self):
        self.comm = serial.Serial(self.port, 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
    
    def open(self):
        if not self.comm.isOpen():
            self.comm.open()
                
    def close(self):
        if self.comm and self.comm.is_open:
            self.comm.close()
    
    def read(self):
        self.comm.flushInput()
        
        self.comm.write(commands['read'])
        sleep(0.05)
        
        if self.comm.in_waiting > 0:
            data = self.comm.read(self.comm.in_waiting)
            sleep(0.05)
            value = int.from_bytes(data[3:5], byteorder='big')
        else:
            raise SensorError('No response from CO2 sensor. Is it connected?')
        
        self.comm.flushOutput()

        return value
    
    def disable_ABC(self):
        self.comm.flushInput()
        
        self.comm.write(commands['ABC_disable'])
        sleep(0.05)
        
        if self.comm.in_waiting > 0:
            data = self.comm.read(self.comm.in_waiting)
        
            self.ABC_on = not (data == commands['ABC_disable'])
        
        self.comm.flushOutput()

    
    def set_ABC_period(self, period_hrs=180):
        self.comm.flushInput()
        
        period_hex = int.to_bytes(int(period_hrs), 2, byteorder='big')
        
        msg = commands['ABC_enable_start'] + period_hex
        msg += calculate_crc16(msg)
        
        print(msg)
        self.comm.write(msg)
        sleep(0.05)
        
        if self.comm.in_waiting > 0:
            data = self.comm.read(self.comm.in_waiting)
        
            self.ABC_on = data == msg
        
        self.comm.flushOutput()

    def get_ABC_period(self):
        self.comm.flushInput()
        
        self.comm.write(commands['ABC_get_period'])
        sleep(0.05)
        
        if self.comm.in_waiting > 0:
            data = self.comm.read(self.comm.in_waiting)
            period = int.from_bytes(data[3:5], byteorder='big')
        else:
            raise SensorError('No response from CO2 sensor. Is it connected?')
        
        self.comm.flushOutput()
        
        return period
    
    
    def close(self):
        self.comm.close()