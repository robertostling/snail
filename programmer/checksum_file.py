import sys

def checksum(data):
    s = 0xabba
    for x in data:
        s = (s + (s << 3) + (s << 9) + x) & 0xffff
    return s

with open(sys.argv[1]) as f:
    header = f.readline()
    assert header.strip() == 'v2.0 raw'
    data = [int(n, 16) for n in f.read().split()]
    print('Read', len(data), 'bytes')
    print('Checksum: %04x' % checksum(data))


