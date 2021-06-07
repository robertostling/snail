"""CPU simulator

This assumes microcode is present in ucode_a.hex and ucode_b.hex
as produced by ucode.py.

Currently rather simple, with lots of output to stdout for later filtering.
"""

import array

def load_hex(filename):
    def decode_bytes(s):
        if '*' in s:
            n, value = s.split('*')
            return [int(value, 16)] * int(n)
        else:
            return [int(s, 16)]

    with open(filename, 'r') as f:
        header = next(f).strip()
        if header != 'v2.0 raw':
            raise ValueError('Only v2.0 raw hex file supported')
        data = []
        for line in f:
            for s in line.split():
                data.extend(decode_bytes(s))

    return data


def hexdump(a, start, end):
    k = 16
    for i in range(start, end, k):
        print('%04x ' % i, ' '.join(['%02x' % a[j] for j in range(i, i+k)]))


class MicroSimulator:
    def __init__(self, urom_prefix, ram_path=None):
        self.ram = array.array('B', [0]*0x10000)
        if ram_path is not None:
            self.load_ram(load_hex(ram_path))
        self.roma = array.array('B', load_hex(urom_prefix+'_a.hex'))
        self.romb = array.array('B', load_hex(urom_prefix+'_b.hex'))
        # Registers X, A, T
        self.x = 0
        self.a = 0
        self.t = 0
        # Input signals
        self.in0 = 0
        self.in1 = 0
        # Output signals
        self.io = 0
        # Output latch
        self.out = 0
        # Current state
        self.state = 0
        # Total number of cycles during simulation
        self.n_ticks = 0

    def load_ram(self, data):
        assert len(data) <= len(self.ram)
        for i, x in enumerate(data):
            self.ram[i] = x

    def disassemble(self, x):
        reg_n = (x & 0xf8) >> 3
        reg = 'r%d' % reg_n
        reg_value = self.ram[reg_n]
        x_value = (self.x >> 8) & 0xff
        if x & 0x07 == 0x00:
            return '%-3s += x  [%s = 0x%02x; X = 0x%02x]' % (
                    reg, reg, reg_value, x_value)
        elif x & 0x07 == 0x04:
            return 'x &= %-3s  [%s = 0x%02x; X = 0x%02x]' % (
                    reg, reg, reg_value, x_value)
        elif x & 0x07 == 0x02:
            return 'x ^= %-3s  [%s = 0x%02x; X = 0x%02x]' % (
                    reg, reg, reg_value, x_value)
        elif x & 0x07 == 0x06:
            return 'x = %-3s   [%s = 0x%02x; X = 0x%02x]' % (
                    reg, reg, reg_value, x_value)
        elif x & 0x07 == 0x01:
            return '%-3s = x   [%s = 0x%02x; X = 0x%02x]' % (
                    reg, reg, reg_value, x_value)
        elif x & 0x07 == 0x05:
            return 'x = [x:%-3s] [%s = 0x%02x; X = 0x%02x, m = 0x%02x]' % (
                    reg, reg, reg_value, x_value,
                    self.ram[(x_value<<8)|reg_value])
        elif x & 0x0f == 0x0b:
            return 'I/O   [X = 0x%02x, in0 = %d, in1 = %d]' % (
                    x_value, self.in0, self.in1)
        elif x & 0x0f == 0x03:
            reg1 = 'r%d' % (reg_n|1)
            address = (self.ram[reg_n|1]<<8)|self.ram[reg_n]
            return '[%s:%s] = x   [%s:%s = 0x%04x; X = 0x%02x]' % (
                    reg1, reg, reg1, reg, address, x_value)
        elif x & 0x0f == 0x07:
            return 'x = x>>4 | 0x%x   [X = 0x%02x]' % (
                    (x>>4)&0x0f, x_value)

        elif x & 0xcf == 0x8f:
            return 'jumpz %s:r2   [%s:r2 = 0x%04x; X = 0x%02x]' % (
                    reg, reg, (reg_value<<8)|self.ram[2], x_value)
        else:
            raise ValueError('Invalid opcode')


    def get_state(self):
        a0 = self.a & 1
        x0 = self.x & 1
        t0 = self.t & 1
        rom_adr = (self.state << 5) | (t0 << 2) | (a0 << 1) | x0
        ram_adr = self.a
        ram_data = (self.x & 0xff00) >> 8
        roma = self.roma[rom_adr]
        romb = self.romb[rom_adr]

        shx = roma & 1
        x = (roma >> 1) & 1
        sha = (roma >> 2) & 1
        a = (roma >> 3) & 1
        sht = (roma >> 4) & 1
        load = (roma >> 5) & 1
        store = (roma >> 6) & 1

        ins = ['%02x:'%self.state, 'A0=%d'%a0, 'X0=%d'%x0, 'T0=%d'%t0]
        outs = [('%d->X'%x if shx else '    '),
                ('%d->A'%a if sha else '    '),
                '0->T' if sht else '    ',
                ('%02x=>T' % self.ram[self.a] if load else '     '),
                ('%02x=>[A]' % ram_data if store else '       '),
                'X=%04x' % self.x,
                'A=%04x' % self.a,
                'T=%02x' % self.t,
                ]

        return ' '.join(ins) + ' | ' + ' '.join(outs)


    def tick(self):
        a0 = self.a & 1
        x0 = self.x & 1
        t0 = self.t & 1
        in0 = self.in0
        in1 = self.in1
        assert in0 in (0, 1)
        assert in1 in (0, 1)
        rom_adr = (self.state << 5) | (in1 << 4) | (in0 << 3) \
                | (t0 << 2) | (a0 << 1) | x0
        ram_adr = self.a
        ram_data = (self.x & 0xff00) >> 8
        roma = self.roma[rom_adr]
        romb = self.romb[rom_adr]

        shx = roma & 1
        x = (roma >> 1) & 1
        sha = (roma >> 2) & 1
        a = (roma >> 3) & 1
        sht = (roma >> 4) & 1
        load = (roma >> 5) & 1
        store = (roma >> 6) & 1
        io = (roma >> 7) & 1

        self.io = io

        # Note: low byte of X goes to output latch, high byte goes to data bus
        if io: self.out = self.x & 0xff

        if shx: self.x = (self.x >> 1) | (x << 15)
        if sha: self.a = (self.a >> 1) | (a << 15)
        if sht: self.t = (self.t >> 1)

        if load and store:
            raise ValueError('load and store signals both asserted!')

        if load: self.t = self.ram[ram_adr]

        if store: self.ram[ram_adr] = ram_data

        self.state = romb

        self.n_ticks += 1


    def run(self, callback):
        while callback(self):
            self.tick()



def main():
    import sys

    def step(sim):
        print(sim.get_state())
        if sim.state == 0:
            sim.n_ops += 1
            ip = (sim.ram[1]<<8) + sim.ram[0]
            #if ip > 0x24: return False
            op = sim.ram[ip+1]
            #print('IP+1=%04x  OP=%02x' % (ip+1, op))
            print('OP %d:%d %04x: %02x  %s' % (
                sim.n_ticks, sim.n_ops, ip+1, op, sim.disassemble(op)))
            if sim.n_ops > 1000: return False
        if sim.io:
            print('OUT 0x%02x' % sim.out)
        #print(sim.n_ticks, 'state %02x' % sim.state)
        return True
        #return sim.n_ticks < 100

    sim = MicroSimulator('./ucode', sys.argv[1])
    sim.n_ops = 0

    sim.run(step)

    hexdump(sim.ram, 0, len(sim.ram))

if __name__ == '__main__': main()
