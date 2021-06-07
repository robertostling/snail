"""Microcode for the CPU

Running this produces two files:
    ucode_a.hex     microinstruction
    ucode_b.hex     next state

These should be written to the two 8kB ROMs used for microcode store.
"""

from uasm import Microcode

# Instruction set:
#
# aaaaa000      [ZP] = X + [ZP] ; X = carry
# aaaaa100      X = X & [ZP]
# aaaaa010      X = X ^ [ZP]
# aaaaa110      X = [ZP]
# aaaaa001      [ZP] = X
# aaaaa101      X = [X:[ZP]]
# aaaaa011      [[ZP+1]:[ZP]] = X           (require: ZP = xxxx0)
# ----1011      PORT = X (signal: XL -> PORT), X = 2 input bits
# nnnn0111      X = (X >> 4) | nnnn0000
# aaaaa111      [ZP]:[2] -> IP   if X = 0   (require: ZP = 10xx1)
#


u = Microcode()

# Label for reset state
# currently no specific reset code, go straight to fetch and assume IP has
# been initialized
label_reset = u.here()

# Label for the start of a new instruction
label_fetch = u.here()

# Memory location where IP is stored
# Do not change! These values are assumed in several places.
IPL = 0
IPH = 1

# A = IPL (address to low byte of IP)
for i in range(16): u.set(sha=1, a=(IPL>>i)&1)
# T = [IPL]
u.set(load=1)
# compute T+1 and shift into high byte of X
# bit 0, always add 1. If input is 1, will have carry, skip next state
u.set(x=(lambda **ins: ins['t0']^1), sht=1, shx=1,
      goto=(lambda **ins: u.here() + 1 + ins['t0']))
for n in range(1,7):
    # bit N, no carry
    u.set(x=(lambda **ins: ins['t0']), sht=1, shx=1, goto=u.here() + 2)
    # bit N, carry
    u.set(x=(lambda **ins: ins['t0']^1), sht=1, shx=1,
          goto=(lambda **ins: u.here() + 1 + ins['t0']))
# carry will not propagate to high byte of IP, so bit 7 is a special case
# bit 7, no carry
u.set(x=(lambda **ins: ins['t0']), sht=1, shx=1, goto=u.here() + 2)
# bit 7, carry
u.set(x=(lambda **ins: ins['t0']^1), sht=1, shx=1)
# write back low byte of IP+1 to RAM
u.set(store=1)
# A = IPH (address to high byte of IP)
for i in range(16): u.set(sha=1, a=(IPH>>i)&1)
# swap bytes of X, restoring old value of XH, XL is low byte of IP+1
# at the same time, set T = [IPH]
for _ in range(8): u.set(load=1, shx=1, x=(lambda **ins: ins['x0']))
# shift XL into AH
for _ in range(8): u.set(shx=1, sha=1, a=(lambda **ins: ins['x0']))
# shift AH into AL, T into AH, so that A becomes IP+1 (except no carry into
# high byte)
for _ in range(8): u.set(sht=1, sha=1, a=(lambda **ins: ins['t0']))
# load instruction byte into T
u.set(load=1)
# T now contains instruction, and we are ready to execute.
# the next step is to shift T into A and pad with 0 bits
# the low 3 (or more) bits of A will then contain the opcode, after they are
# shifted out A will contain a 
for _ in range(8): u.set(sht=1, sha=1, a=(lambda **ins: ins['t0']))
for _ in range(8): u.set(sha=1, a=0)

# decode instruction
# the forward references here are handled later, by calling u.set() again once
# the targets are known
label_xxx = u.here()
u.set(sha=1, a=0)
label_xx0 = u.here()
u.set(sha=1, a=0)
label_x00 = u.here()
u.set(sha=1, a=0)
label_x10 = u.here()
u.set(sha=1, a=0)
label_xx1 = u.here()
u.set(sha=1, a=0)
label_x01 = u.here()
u.set(sha=1, a=0)
label_x11 = u.here()
u.set(sha=1, a=0)

# individual instructions are defined below
# note that the value of X is contained in XL at this stage, but should be
# left in XH on exit

label_000 = u.here()
# aaaaa000      [ZP] = X + [ZP] ; X = carry
u.set(load=1)
for _ in range(8):
    # no carry in
    u.set(x=(lambda **ins: ins['t0']^ins['x0']), sht=1, shx=1,
          goto=(lambda **ins: u.here() + 2 + (ins['t0']&ins['x0'])))
    # carry in
    u.set(x=(lambda **ins: ins['t0']^ins['x0']^1), sht=1, shx=1,
          goto=(lambda **ins: u.here() + 1 + (ins['t0']|ins['x0'])))
# write result to ZP, and set X to the result
# carry = 0
u.set(store=1, x=0, shx=1, goto=u.here() + 2)
# carry = 1
u.set(store=1, x=1, shx=1)
u.set(x=0, shx=1)
# After this point, we shift 6 zero bits into X and return to fetch
# The I/O instruction jumps here
label_shift_x_6 = u.here()
for _ in range(5): u.set(x=0, shx=1)
u.set(x=0, shx=1, goto=label_fetch)


label_100 = u.here()
# aaaaa100      X = X & [ZP]
u.set(load=1)
for _ in range(7): u.set(x=(lambda **ins: ins['t0']&ins['x0']), sht=1, shx=1)
u.set(x=(lambda **ins: ins['t0']&ins['x0']), sht=1, shx=1, goto=label_fetch)


label_010 = u.here()
# aaaaa010      X = X ^ [ZP]
u.set(load=1)
for _ in range(7): u.set(x=(lambda **ins: ins['t0']^ins['x0']), sht=1, shx=1)
u.set(x=(lambda **ins: ins['t0']^ins['x0']), sht=1, shx=1, goto=label_fetch)


label_110 = u.here()
# aaaaa110      X = [ZP]
u.set(load=1)
label_t_to_x = u.here()
for _ in range(7): u.set(x=(lambda **ins: ins['t0']), sht=1, shx=1)
u.set(x=(lambda **ins: ins['t0']), sht=1, shx=1, goto=label_fetch)


label_001 = u.here()
# aaaaa001      [ZP] = X
for _ in range(8): u.set(shx=1, x=(lambda **ins: ins['x0']))
u.set(store=1, goto=label_fetch)


label_101 = u.here()
# aaaaa101      X = [X:[ZP]]
# T = [ZP]
u.set(load=1)
# A = X:[ZP]
for _ in range(8): u.set(sht=1, sha=1, a=(lambda **ins: ins['t0']))
for _ in range(8): u.set(shx=1, sha=1, a=(lambda **ins: ins['x0']))
# T = [X:[ZP]]
u.set(load=1, goto=label_t_to_x)
# X = T
#for _ in range(7): u.set(shx=1, sht=1, x=(lambda **ins: ins['t0']))
#u.set(shx=1, sht=1, x=(lambda **ins: ins['t0']), goto=label_fetch)


label_1011 = u.here()
# ----1011      PORT = X (signal: XL -> PORT), X = 2 input bits
u.set(shx=1, x=(lambda **ins: ins['in0']), io=1)
u.set(shx=1, x=(lambda **ins: ins['in1']), goto=label_shift_x_6)

label_011 = u.here()
# aaaaa011      [[ZP+1]:[ZP]] = X

# T = [ZP]
u.set(load=1, goto=(lambda **ins: label_1011 if ins['a0'] else u.here() + 1))
# X = [ZP]:X
# A = A|1
# ... unless a0 is set, in that case the instruction is actually I/O
u.set(shx=1, sha=1, x=(lambda **ins: ins['x0']), a=1)
for _ in range(7): u.set(shx=1, sha=1, x=(lambda **ins: ins['x0']),
                         a=(lambda **ins: ins['a0']))
for _ in range(8): u.set(shx=1, sht=1, sha=1, x=(lambda **ins: ins['t0']),
                         a=(lambda **ins: ins['a0']))
# T = [ZP+1]
u.set(load=1)
# X = X:[ZP]
for _ in range(8): u.set(shx=1, x=(lambda **ins: ins['x0']))
# A = [ZP+1]:[ZP]
# X = -:X
for _ in range(8): u.set(sha=1, shx=1, a=(lambda **ins: ins['x0']))
# X = X:-
for _ in range(8): u.set(sha=1, sht=1, shx=1, a=(lambda **ins: ins['t0']),
                         x=(lambda **ins: ins['x0']))
u.set(store=1, goto=label_fetch)


# aaaaa111      [ZP]:[2] -> IP   if X = 0  (assume ZP = 10xx1)

label_1111 = u.here()
# T = [ZP]   (done at label_111)
# shift out low 3 bits of A (ZP address), so we reach A = 2
# at the same time, shift T into XH, due to be stored in [1]
# abort the process if any bit in X is non-zero
# Note that the lowest bit of the ZP address has already been shifted out
# before we get here.
u.set(a=0, sha=1, x=(lambda **ins: ins['t0']), shx=1, sht=1,
      goto=(lambda **ins: label_fetch if ins['x0'] else u.here() + 1))
u.set(a=0, sha=1, x=(lambda **ins: ins['t0']), shx=1, sht=1,
      goto=(lambda **ins: label_fetch if ins['x0'] else u.here() + 1))
#u.set(a=0, sha=1, x=(lambda **ins: ins['t0']), shx=1, sht=1,
#      goto=(lambda **ins: label_fetch if ins['x0'] else u.here() + 1))
for _ in range(6):
    u.set(x=(lambda **ins: ins['t0']), shx=1, sht=1,
          goto=(lambda **ins: label_fetch if ins['x0'] else u.here() + 1))
# XH = new IPH to be stored at [1], now load [2] into T
# shift another 0 bit into A, so A = 1
u.set(load=1, a=0, sha=1)
# store IPH, and shift a final 0 bit into A so A = 0
# shift T into X
u.set(store=1, x=(lambda **ins: ins['t0']), shx=1, sht=1)
for _ in range(6):
    u.set(x=(lambda **ins: ins['t0']), shx=1, sht=1)
u.set(x=(lambda **ins: ins['t0']), a=0, shx=1, sht=1, sha=1)
u.set(store=1, goto=label_fetch)


label_111 = u.here()
# Could be one of the following:
# nnnn0111      X = (X >> 4) | nnnn0000
# aaaaa111      [ZP]:[2] -> IP   if X = 0  (assume ZP = 10xx1)
# Shift out the next bit, branching to the jump instruction in case it is set,
# otherwise continue by loading literal.
# Load ZP into T, will only be used by the jump instruction.
u.set(load=1, a=0, sha=1,
      goto=(lambda **ins: label_1111 if ins['a0'] else u.here() + 1))
for _ in range(8): u.set(shx=1, x=(lambda **ins: ins['x0']))
for _ in range(3): u.set(shx=1, sha=1, x=(lambda **ins: ins['a0']))
u.set(shx=1, sha=1, x=(lambda **ins: ins['a0']), goto=label_fetch)

# resolve forward references during lookup
u.set(state=label_xxx, sha=1, a=0,
      goto=(lambda **ins: label_xx1 if ins['a0'] else label_xx0))
u.set(state=label_xx0, sha=1, a=0,
      goto=(lambda **ins: label_x10 if ins['a0'] else label_x00))
u.set(state=label_x00, sha=1, a=0,
      goto=(lambda **ins: label_100 if ins['a0'] else label_000))
u.set(state=label_x10, sha=1, a=0,
      goto=(lambda **ins: label_110 if ins['a0'] else label_010))
u.set(state=label_xx1, sha=1, a=0,
      goto=(lambda **ins: label_x11 if ins['a0'] else label_x01))
u.set(state=label_x01, sha=1, a=0,
      goto=(lambda **ins: label_101 if ins['a0'] else label_001))
u.set(state=label_x11, sha=1, a=0,
      goto=(lambda **ins: label_111 if ins['a0'] else label_011))


u.status()
u.save('ucode')

