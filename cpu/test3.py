"""Loop test"""

import asm

def program(a):
    a.org = 0
    a.dword(a['start']-1)

    a.org = 0x20
    a['start'] = a.org

                    # r17:r2 = branch address for loop
    a.store_label('loop', 17, 2)

    a.lit(5)
    a.store(4)      # r4 = counter

    a['loop'] = a.org

    a.load(4)
    a.io()

    a.lit(0xff)
    a.add(4)        # r4 -= 1  X = 0 if no carry, i.e. when counter was 0

    a.store(5)
    a.lit(0x01)
    a.bxor(5)        # X = carry ^ 1

    a.jumpz(17, 2)

    a['inf_loop'] = a.org
    a.lit(a['inf_loop']-1)
    a.store(0)

    a.org = 0x1234
    a.dbyte(0xab)

a = asm.Assembler()
a.assemble(program)
a.save_v2raw('test3.hex')

