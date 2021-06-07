import time
import serial
import sys

if __name__ == '__main__':
    device = '/dev/ttyUSB0'
    ser = serial.Serial(device, baudrate=9600, timeout=1)

    data = []
    ser.write(b'R')
    for i in range(0x2000):
        ser.write(b'L')
        reply = ser.readline()
        assert reply[:1] == b'L', reply
        x = int(reply[1:], 16)
        print(str(b'%04x: %02x %s' % (i, x, reply), 'utf-8'))
        data.append(x)

    ser.close()

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w') as f:
            print('v2.0 raw', file=f)
            print(' '.join(['%02x' % x for x in data]), file=f)


