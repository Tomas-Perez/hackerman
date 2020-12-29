import math

def sixth_unpack(pos, debug=False):
    pos = pos + 1
    MAGIC_ARRAY = [
        5,
        0.516666668800000006279,
        4,
        8.12500003699999950868,
        3,
        45.8333335800000014615,
        2,
        109.875000700000001075,
        99.6500009300000044732,
        83.9999996800000019448,
    ]
    a = math.pow(pos, MAGIC_ARRAY[0]) * MAGIC_ARRAY[1]
    if debug:
        print("0x80493b2 | ST0:", a)
    b = math.pow(pos, MAGIC_ARRAY[2]) * MAGIC_ARRAY[3]
    a = a - b
    if debug:
        print("0x80493df | ST0:", a)
    c = math.pow(pos, MAGIC_ARRAY[4]) * MAGIC_ARRAY[5]
    a = c + a
    if debug:
        print("0x804940c | ST0:", a)
    d = math.pow(pos, MAGIC_ARRAY[6]) * MAGIC_ARRAY[7]
    a = a - d
    if debug:
        print("0x804943b | ST0:", a)
    e = MAGIC_ARRAY[8] * pos
    a = e + a
    if debug:
        print("0x8049448 | ST0:", a)
    a += MAGIC_ARRAY[9]
    if debug:
        print("0x8049450 | ST0:", a)
    return chr(int(a))

def eighth_unpack(char, long, debug=False):
    MAX_LONG = 9223372036854775808
    char_int = ord(char)
    calculation = math.pow(char_int, math.sqrt(char_int))
    if calculation < MAX_LONG:
        calculation = int(calculation)
        if debug:
            print("calculation if < MAX_LONG:", hex(calculation))
    else:
        calculation -= MAX_LONG
        if calculation > MAX_LONG:
            calculation = 0 # overflow when going from FPU to normal registers, ends up going to 0.
        else:
            calculation = int(calculation)
            calculation ^= 0x8000000000000000
        if debug:
            print("calculation if >= MAX_LONG:", hex(calculation))
    calculation += 0x15
    calculation ^= long
    eax = calculation & 0xffffffff
    edx = (calculation & 0xffffffff00000000) >> 32
    eax |= edx
    if debug:
        print('final eax:', hex(eax))
    if eax == 0:
        return True
    else:
        return False

def seventh_unpack(pos):
    MAGIC_ARRAY = [
        0x0000001ca66fe7dd,
        0x00000227357afcf8,
        0x0000000000000015,
        0x0000016c5c156c54,
        0x0000001ca66fe7dd,
        0x0000009de93ece66,
        0x0000016c5c156c54,
        0x0000016c5c156c54,
        0x00000756f3444241,
        0x000000014660a4c5,
        0x0000001ca66fe7dd,
    ]

    printable_chars = [chr(i) for i in range(127)]

    for c in printable_chars:
        if eighth_unpack(c, MAGIC_ARRAY[pos - 6]):
            return c

def ninth_unpack(pos, get_char_for_pos, debug=False):
    MAGIC_ARRAY = [
        0x0b,
        0x4c,
        0x0f,
        0x00,
        0x01,
        0x16,
        0x10,
        0x07,
        0x09,
        0x38,
        0x00,
    ]

    prev_char = get_char_for_pos(pos-1)  
    magic_number = MAGIC_ARRAY[pos-16]      
    result = chr(ord(prev_char) ^ magic_number)
    if debug:
        print('---------------')
        print('getting char for pos', pos)
        print('prev_char', prev_char)
        print('magic_number', hex(magic_number))
        print('result', result)
        print('---------------')
    return result

def get_char_for_pos(pos):
    if pos in range(0, 6):
        return sixth_unpack(pos)
    elif pos in range(6, 17):
        return seventh_unpack(pos)
    else:
        return ninth_unpack(pos, get_char_for_pos)

if __name__ == "__main__":
    flag_size = 0x21    # 10th unpack check

    header = "flag{"    # 2nd unpack check
    end = "}"           # 3rd unpack check

    content_len = flag_size - len(header) - len(end)
    content = [get_char_for_pos(i) for i in range(content_len)]

    print("\"" + header + ''.join(content) + end + "\"")
    