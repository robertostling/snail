"""Memory access test"""

import asm

def program(a):
    a.org = 0
    a.dword(a['start']-1)

    a.org = 0x20
    a['start'] = a.org

    a.lit(0x34)
    a.store(10)
    a.lit(0x12)
    a.store(11)     # r10:r11 = 0x1234

    a.load(11)
    a.iload(10)     # X = [0x1234]

    a.store(12)
    a.lit(0x11)
    a.add(12)       # r12 = [0x1234] + 0x11

    a.load(12)
    a.istore(10, 11)

    a['loop'] = a.org
    a.lit(a['loop']-1)
    a.store(0)

    a.org = 0x1234
    a.dbyte(0xab)

a = asm.Assembler()
a.assemble(program)
a.save_v2raw('test2.hex')

