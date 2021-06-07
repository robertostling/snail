"""Basic test program for the assembler/CPU"""

import asm

def program(a):
    a.org = 0
    a.dword(a['start']-1)

    a.org = 0x20
    a['start'] = a.org
    a.lit(0xc3)
    a.store(10)
    a.lit(0x18)
    a.add(10)
    a.store(11)
    a['loop'] = a.org
    a.lit(a['loop']-1)
    a.store(0)

a = asm.Assembler()
a.assemble(program)
a.save_v2raw('test1.hex')

