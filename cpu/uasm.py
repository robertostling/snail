"""Microcode assembler

Used by ucode.py to produce the two microcode files needed.
"""

import array

class Microcode:
    def __init__(self):
        self.next_state = 0
        self.roma = array.array('B', [0]*0x2000)
        self.romb = array.array('B', [0]*0x2000)

    def here(self):
        return self.next_state

    def status(self):
        print('Microcode status: %d/256 states used' % self.next_state)

    def set(self, state=None, **kwargs):
        """Set the action of a given microcode state

        Args:
            state -- int from 0 to 0xff
            shx -- value of shx bit, default 0, or callable that returns
                   0 or 1 given kwargs x0, a0, t0 (input bits)
            x, sha, a, sht, load, store, io -- like shx
            goto -- state to jump to, or undefined for self.next_state,
                    or callable(x0=x, a0=y, t0=z) that computes the next state
                    given the input bits x, y, z

        Returns:
            int, actual state modified
        """
        allocate = (state is None)
        if allocate:
            state = self.next_state
        else:
            print('INFO: state %d redefined' % state)

        fields = 'shx x sha a sht load store io'.split()
        for k, v in kwargs.items():
            if k not in fields + ['goto']:
                raise ValueError('Unknown parameter: ' + k)

        for in_bits in range(0x20):
            x0 = (in_bits >> 0) & 1
            a0 = (in_bits >> 1) & 1
            t0 = (in_bits >> 2) & 1
            in0 = (in_bits >> 3) & 1
            in1 = (in_bits >> 4) & 1
            ins = {}
            for k, v in kwargs.items():
                ins[k] = v(x0=x0, a0=a0, t0=t0, in0=in0, in1=in1) \
                         if callable(v) else v
            #adr = (state << 5) | (t0 << 2) | (a0 << 1) | x0
            adr = (state << 5) | in_bits
            roma = ins.get('shx', 0) | \
                   (ins.get('x', 0) << 1) | \
                   (ins.get('sha', 0) << 2) | \
                   (ins.get('a', 0) << 3) | \
                   (ins.get('sht', 0) << 4) | \
                   (ins.get('load', 0) << 5) | \
                   (ins.get('store', 0) << 6) | \
                   (ins.get('io', 0) << 7)
            if allocate:
                romb = ins.get('goto', self.next_state+1)
            else:
                romb = ins['goto']
            assert 0 <= romb <= 0xff
            self.roma[adr] = roma
            self.romb[adr] = romb

        if allocate:
            self.next_state += 1

        return state

    def save_v2raw(self, filename, a):
        with open(filename, 'w') as f:
            print('v2.0 raw', file=f)
            print(' '.join(['%02x' % x for x in a]), file=f)

    def save(self, filename_prefix):
        self.save_v2raw(filename_prefix + '_a.hex', self.roma)
        self.save_v2raw(filename_prefix + '_b.hex', self.romb)

