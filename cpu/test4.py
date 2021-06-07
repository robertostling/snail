"""Prototype FORTH inner interpreter"""

import asm

IPL = 0     # hardware instruction pointer
IPH = 1
JZL = 2     # low byte of jumpz target
DPL = 4     # data stack pointer
DPH = 5
RPL = 6     # return stack pointer
RPH = 7
TPL = 8     # threaded instruction pointer
TPH = 9
WL = 10     # W register
WH = 11
JZH = 17    # high byte of jumpz target
NEXTL = 18  # address of NEXT primitive
NEXTH = 19
TEMP0 = 20
CONST0 = 30 # always 0
CONST1 = 31 # always 1

def program(a):
    a.org = 0
    a.dword(a['start']-1)

    a.org = 0x20
    a['start'] = a.org

    # initialize constant registers
    a.lit(1)
    a.store(CONST1)
    a.bxor(CONST1)
    a.store(CONST0)

    # return stack pointer starts at 0xfe00
    # data stack pointer starts at 0xff00
    a.store(RPL)
    a.store(DPL)
    a.lit(0xfe)
    a.store(RPH)
    a.shiftlit(0xf)
    a.store(DPH)

    a.store_jump_label('next', NEXTH, NEXTL)

    a.store_label('example', TPH, TPL)

    a['next'] = a.org
    # [TP] -> W
    # TP += 2
    # JMP [W]
    # W += 2    (note: this increment is not in orthodox FORTH interpreters)
    #
    # [TP] -> WL
    a.load(TPH)
    a.iload(TPL)
    a.store(WL)
    # TP += 1
    a.load(CONST1)
    a.add(TPL)
    a.add(TPH)
    # [TP] -> WH
    a.load(TPH)
    a.iload(TPL)
    a.store(WH)
    # [W] -> JZL  (note: X already contains WH)
    a.iload(WL)
    a.store(JZL)
    # TP += 1
    a.load(CONST1)
    a.add(TPL)
    a.add(TPH)
    # W += 1
    a.load(CONST1)
    a.add(WL)
    a.add(WH)
    # [W] -> JZH
    a.load(WH)
    a.iload(WL)
    a.store(JZH)
    # W += 1
    a.load(CONST1)
    a.add(WL)
    a.add(WH)
    # jump to [W]
    a.load(CONST0)
    a.jumpz(JZH, JZL)
 
    a['enter'] = a.org
    # TP -> [RP]
    # RP += 2
    a.load(TPL)
    a.istore(RPH, RPL)
    a.load(CONST1)
    a.add(RPL)
    a.add(RPH)
    a.load(TPH)
    a.istore(RPH, RPL)
    a.load(CONST1)
    a.add(RPL)
    a.add(RPH)
    # W -> TP
    a.load(WL)
    a.store(TPL)
    a.load(WH)
    a.store(TPH)
    # NEXT
    a.load(NEXTL)
    a.store(JZL)
    a.load(CONST0)
    a.jumpz(NEXTH, JZL)
    
    a['exit'] = a.org
    a.dword(a.org+2-1)
    a.lit(0xff)
    a.add(RPL)
    # TODO: 16-bit subtraction, if needed
    a.load(RPH)
    a.iload(RPL)
    a.store(TPH)

    a.lit(0xff)
    a.add(RPL)
    # TODO: 16-bit subtraction, if needed
    a.load(RPH)
    a.iload(RPL)
    a.store(TPL)

    # NEXT
    a.load(NEXTL)
    a.store(JZL)
    a.load(CONST0)
    a.jumpz(NEXTH, JZL)


    a['branch'] = a.org
    a.dword(a.org+2-1)
    a.load(TPH)
    a.iload(TPL)
    a.store(TEMP0)
    a.load(CONST1)
    a.add(TPL)
    a.add(TPH)
    a.load(TPH)
    a.iload(TPL)
    a.store(TPH)
    a.load(TEMP0)
    a.store(TPL)
    # NEXT
    a.load(NEXTL)
    a.store(JZL)
    a.load(CONST0)
    a.jumpz(NEXTH, JZL)


    # EXAMPLE DEFINITIONS
    a['example'] = a.org
    # NOTE: we put TP at 'example' at the start, so no enter needed for this
    # test
    #a.dword(a['enter']-1)
    a['example_loop'] = a.org
    a.dword(a['out_dead'])
    a.dword(a['branch'])
    a.dword(a['example_loop'])
    
    a['out_dead'] = a.org
    a.dword(a['enter']-1)
    a.dword(a['out_de'])
    a.dword(a['out_ad'])
    a.dword(a['exit'])

    a['out_de'] = a.org
    a.dword(a.org+2-1)
    a.lit(0xde)
    a.io()
    # NEXT
    a.load(NEXTL)
    a.store(JZL)
    a.load(CONST0)
    a.jumpz(NEXTH, JZL)


    a['out_ad'] = a.org
    a.dword(a.org+2-1)
    a.lit(0xad)
    a.io()
    # NEXT
    a.load(NEXTL)
    a.store(JZL)
    a.load(CONST0)
    a.jumpz(NEXTH, JZL)



a = asm.Assembler()
a.assemble(program)
a.save_v2raw('test4.hex')
for label, n in sorted(a.defined_consts.items()):
    print('%-16s 0x%x' % (label, n))

