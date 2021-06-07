import time
import serial
import sys

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        header = f.readline()
        assert header.strip() == 'v2.0 raw'
        data = [int(n, 16) for n in f.read().split()]
        print('Read', len(data), 'bytes')

    device = '/dev/ttyUSB0'
    ser = serial.Serial(device, baudrate=9600, timeout=1)

    ser.write(b'R')
    ser.write(b'R')
    for i, x in enumerate(data):
        cmd = (b'W%02x' % x).upper()
        assert len(cmd) == 3
        ser.write(cmd)
        ack = ser.readline().strip()
        print(str(b'%04x: %02x %s %s' % (i, x, ack, cmd), 'utf-8'))
        if int(ack[1:], 16) != x:
            print('ERROR')
            sys.exit(1)

    ser.close()

