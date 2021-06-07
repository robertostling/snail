import time
import serial

if __name__ == '__main__':
    device = '/dev/ttyUSB0'
    ser = serial.Serial(device, baudrate=9600, timeout=15)

    ser.write(b'S')
    text = ser.readline()
    print(str(text, 'utf-8'))

    ser.close()

