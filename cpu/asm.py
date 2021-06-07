"""Assembler for the snail CPU

To be used from within Python, see test*.py for examples.
"""

class Assembler:
    def __init__(self, mem_size=0x10000):
        self.mem_size = mem_size
        self.defined_consts = {}

    def reset(self):
        """Call before each new pass"""
        self.org = 0x20
        self.deferred_consts = set()
        self.conflict_consts = set()
        self.data = {}

    def need_pass(self):
        """Return True iff a new pass is needed"""
        return len(self.deferred_consts) + len(self.conflict_consts) > 0

    def __getitem__(self, x):
        if x in self.defined_consts:
            return self.defined_consts[x]
        else:
            self.deferred_consts.add(x)
            return 0

    def __setitem__(self, x, y):
        if x in self.defined_consts:
            if self.defined_consts[x] != y:
                self.conflict_consts.add(x)
        self.defined_consts[x] = y

    def write_byte(self, x):
        assert 0 <= x <= 0xff
        assert 0 <= self.org < self.mem_size
        if self.org in self.data:
            raise ValueError('Overwriting 0x%04x' % self.org)
        self.data[self.org] = x
        self.org += 1

    def assemble(self, f):
        n_passes = 0
        while True:
            self.reset()
            f(self)
            n_passes += 1
            if not self.need_pass(): break
            if n_passes >= 100:
                raise ValueError('Giving up after '+str(n_passes)+' passes')
        print('Assembly complete:', n_passes, 'passes')
        return self.data

    def add(self, zp):
        assert 0 <= zp <= 0x1f
        self.write_byte(zp<<3)

    def band(self, zp):
        assert 0 <= zp <= 0x1f
        self.write_byte((zp<<3) | 0x4)

    def bxor(self, zp):
        assert 0 <= zp <= 0x1f
        self.write_byte((zp<<3) | 0x2)

    def load(self, zp):
        assert 0 <= zp <= 0x1f
        self.write_byte((zp<<3) | 0x6)

    def store(self, zp):
        assert 0 <= zp <= 0x1f
        self.write_byte((zp<<3) | 0x1)

    def iload(self, zp):
        assert 0 <= zp <= 0x1f
        self.write_byte((zp<<3) | 0x5)

    def istore(self, zp_h, zp_l):
        assert 0 <= zp_l <= 0x1e
        assert (zp_l & 1) == 0
        assert zp_l + 1 == zp_h
        self.write_byte((zp_l<<3) | 0x3)

    def io(self):
        self.write_byte(0x0b)

    def shiftlit(self, n):
        assert 0 <= n <= 0xf
        self.write_byte((n << 4) | 0x7)

    def lit(self, n):
        assert 0 <= n <= 0xff
        self.shiftlit(n & 0x0f)
        self.shiftlit((n >> 4) & 0x0f)

    def jumpz(self, zp_h, zp_l):
        assert zp_l == 2
        assert (zp_h & 0x19) == 0x11
        self.write_byte((zp_h<<3) | 0x7)

    def dbyte(self, x):
        self.write_byte(x)

    def dword(self, x):
        self.write_byte(x & 0xff)
        self.write_byte((x >> 8) & 0xff)

    def _store_label(self, label, hreg, lreg, offset):
        x = self[label] + offset
        xl = x & 0xff
        xh = (x >> 8) & 0xff
        self.lit(xl)
        self.store(lreg)
        self.lit(xh)
        self.store(hreg)

    def store_jump_label(self, label, hreg, lreg):
        self._store_label(label, hreg, lreg, -1)

    def store_label(self, label, hreg, lreg):
        self._store_label(label, hreg, lreg, 0)
  
    def save_v2raw(self, filename):
        mem = [0]*self.mem_size
        for i, x in self.data.items():
            mem[i] = x
        with open(filename, 'w') as f:
            print('v2.0 raw', file=f)
            for i in range(len(mem)):
                print('%02x' % mem[i], file=f)

