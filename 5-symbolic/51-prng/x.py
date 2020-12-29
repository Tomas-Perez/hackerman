import claripy
import sys

STATE_VECTOR_LENGTH = 624
STATE_VECTOR_M = 397

UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff
TEMPERING_MASK_B = 0x9d2c5680
TEMPERING_MASK_C = 0xefc60000

class MTRand:
    def __init__(self):
        self.mt = [0] * STATE_VECTOR_LENGTH
        self.index = 0

def mag(value):
    mag_array = [0x0, 0x9908b0df]
    return claripy.If(value == 0, claripy.BVV(mag_array[0], 64), claripy.BVV(mag_array[1],64))

def mag_regular(value):
    mag_array = [0x0, 0x9908b0df]
    return mag_array[value]

def m_seedRand(rand: MTRand, seed: int):
    rand.mt[0] = seed & 0xffffffff
    rand.index = 1

    while rand.index < STATE_VECTOR_LENGTH:
        rand.mt[rand.index] = (6069 * rand.mt[rand.index-1]) & 0xffffffff
        rand.index += 1

def getRandLong_regular(rand: MTRand):
    if rand.index < 0 or rand.index >= STATE_VECTOR_LENGTH:
        if rand.index < 0 or rand.index >= STATE_VECTOR_LENGTH + 1:
            m_seedRand(rand, 0x1105)

        kk = 0

        while kk < STATE_VECTOR_LENGTH-STATE_VECTOR_M:
            y = rand.mt[kk + 1] & 0xffffffff
            rand.mt[kk] = rand.mt[kk + STATE_VECTOR_M] ^ (y & LOWER_MASK | (rand.mt[kk] & 0xffffffff) & UPPER_MASK) >> 1 ^ mag_regular(y & 1)
            kk = kk + 1

        while kk < STATE_VECTOR_LENGTH - 1:
            y = rand.mt[kk + 1] & 0xffffffff
            rand.mt[kk] = rand.mt[kk + (STATE_VECTOR_M-STATE_VECTOR_LENGTH)] ^ (y & LOWER_MASK | (rand.mt[kk] & 0xffffffff) & UPPER_MASK) >> 1 ^ mag_regular(y & 1)
            kk = kk + 1

        y = rand.mt[0] & 0xffffffff
        rand.mt[STATE_VECTOR_LENGTH - 1] = rand.mt[STATE_VECTOR_M - 1] ^ (y & LOWER_MASK | (rand.mt[STATE_VECTOR_LENGTH - 1] & 0xffffffff) & UPPER_MASK) >> 1 ^ mag_regular(y & 1)
        rand.index = 0

    iVar1 = rand.index
    rand.index = iVar1 + 1
    uVar2 = rand.mt[iVar1] ^ rand.mt[iVar1] >> 0xb
    uVar2 ^= ((uVar2 << 7) & 0xffffffff) & TEMPERING_MASK_B
    uVar2 ^= ((uVar2 << 0xf) & 0xffffffff) & TEMPERING_MASK_C
    return uVar2 ^ uVar2 >> 0x12

def genRandLong(rand: MTRand):
    if rand.index < 0 or rand.index >= STATE_VECTOR_LENGTH:
        if rand.index < 0 or rand.index >= STATE_VECTOR_LENGTH + 1:
            m_seedRand(rand, 0x1105)

        kk = 0

        while kk < STATE_VECTOR_LENGTH-STATE_VECTOR_M:
            y = rand.mt[kk + 1] & 0xffffffff
            rand.mt[kk] = rand.mt[kk + STATE_VECTOR_M] ^ claripy.LShR((y & LOWER_MASK | (rand.mt[kk] & 0xffffffff) & UPPER_MASK), 1) ^ mag(y & 1)
            kk = kk + 1

        while kk < STATE_VECTOR_LENGTH - 1:
            y = rand.mt[kk + 1] & 0xffffffff
            rand.mt[kk] = rand.mt[kk + (STATE_VECTOR_M-STATE_VECTOR_LENGTH)] ^ claripy.LShR((y & LOWER_MASK | (rand.mt[kk] & 0xffffffff) & UPPER_MASK), 1) ^ mag(y & 1)
            kk = kk + 1

        y = rand.mt[0] & 0xffffffff
        rand.mt[STATE_VECTOR_LENGTH - 1] = rand.mt[STATE_VECTOR_M - 1] ^ claripy.LShR(y & LOWER_MASK | (rand.mt[STATE_VECTOR_LENGTH - 1] & 0xffffffff) & UPPER_MASK, 1) ^ mag(y & 1)
        rand.index = 0

    iVar1 = rand.index
    rand.index = iVar1 + 1
    uVar2 = rand.mt[iVar1] ^ claripy.LShR(rand.mt[iVar1], 0xb)
    uVar2 ^= ((uVar2 << 7) & 0xffffffff) & TEMPERING_MASK_B
    uVar2 ^= ((uVar2 << 0xf) & 0xffffffff) & TEMPERING_MASK_C
    return uVar2 ^ claripy.LShR(uVar2, 0x12)

def sym_solve():

    seed = claripy.BVS("seed", 64)

    rand = MTRand()

    m_seedRand(rand, seed)

    for _ in range(1000):
        genRandLong(rand)

    leak_sym = genRandLong(rand)

    s = claripy.Solver()

    leak = int(input("Enter leak:"), base=16)

    s.add(leak_sym == leak)

    print(hex(s.eval(seed, 1)[0]))

def regular_run():
    seed = int(input("Enter seed:"), base=16)
    rand = MTRand()
    m_seedRand(rand, seed)

    for _ in range(1000):
        getRandLong_regular(rand)

    leak = getRandLong_regular(rand)

    print(f"leak: {hex(leak)}")

if len(sys.argv) >= 2 and sys.argv[1] == "r":
    regular_run()
else:
    sym_solve()
