import claripy

# Does not work, don't know why, just use angr lmao

SIZE = 0x1d

def check_01(key):
    return claripy.And(
        key[5] == ord('-'),
        key[0xb] == ord('-'), 
        key[0x11] == ord('-'),
        key[0x17] == ord('-'),
    )

def check_02(key):
    return claripy.And(
        key[1] - 0x30 < 10,
        key[4] - 0x30 < 10,
        key[6] - 0x30 < 10,
        key[9] - 0x30 < 10,
        key[0xf] - 0x30 < 10,
        key[0x12] - 0x30 < 10,
        key[0x16] - 0x30 < 10, 
        key[0x1b] - 0x30 < 10,
        key[0x1c] - 0x30 < 10,
    )

def check_03(key):
    return claripy.And(
        key[4] - 0x30 == (key[1] - 0x30) * 2 + 1,
        7 < key[4] - 0x30,
        key[9] == (key[4] - (key[1] - 0x30)) + 2,
    )


def check_04(key):
    return (key[0x1b] + key[0x1c]) % 0xd == 8

def check_05(key):
    return (key[0x1b] + key[0x16]) % 0x16 == 0x12

def check_06(key):
    return (key[0x12] + key[0x16]) % 0xb == 5

def check_07(key):
    return (key[0x1c] + key[0x16] + key[0x12]) % 0x1a == 4

def check_08(key):
    return (key[1] + key[6] * key[4]) % 0x29 == 5

def check_09(key):
    uVar1 = claripy.LShR(claripy.LShR(key[0xf] - key[0x1c], 0x1f), 0x1e)
    return ((key[0xf] - key[0x1c]) + uVar1 & 3) - uVar1 == 1

def check_0A(key):
    uVar1 = claripy.LShR(claripy.LShR(key[4] + key[0x16], 0x1f), 0x1e)
    return (key[4] + key[0x16] + uVar1 & 3) - uVar1 == 3

def check_0B(key):
    return claripy.And(
        key[0x14] == ord('B'),
        key[0x15] == ord('B'),
    )

def check_0C(key):
    return (key[6] + key[9] * key[0xf]) % 10 == 1

def check_0D(key):
    iVar1 = key[0x1b] + key[4] + key[0xf] + -0x12
    uVar2 = claripy.LShR(claripy.LShR(iVar1, 0x1f), 0x1c)
    return (iVar1 + uVar2 & 0xf) - uVar2 == 8

def check_0E(key):
    iVar1 = claripy.LShR(key[0x1c] - key[9], 0x1f)
    return ((key[0x1c] - key[9]) - iVar1 & 1) + iVar1 == 1

def check_0F(key):
    return key[0] == ord("M")


key = [claripy.BVS(f'c{i}', 32) for i in range(SIZE)]
s = claripy.Solver()

for c in key: # make sure all chars are printable
    s.add(claripy.And(c >= 0x20, c <= 0x7e))

s.add(check_01(key))
s.add(check_02(key))
s.add(check_03(key))
s.add(check_04(key))
s.add(check_05(key))
s.add(check_06(key))
s.add(check_07(key))
s.add(check_08(key))
s.add(check_09(key))
s.add(check_0A(key))
s.add(check_0B(key))
s.add(check_0C(key))
s.add(check_0D(key))
s.add(check_0E(key))
s.add(check_0F(key))

possible_key = []

for c in key:
    possible_key.append(chr(s.eval(c, 1)[0]))

print(possible_key)
print("".join(possible_key))
