import math

def eighth_unpack(char, other_random_number, number, debug=False):
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
    eax = calculation & 0xffffffff
    edx = (calculation & 0xffffffff00000000) >> 32
    if debug:
        print('eax:', hex(eax))
        print('edx:', hex(edx))
    eax ^= other_random_number
    edx ^= number
    eax |= edx
    if debug:
        print('final eax:', hex(eax))
    if eax == 0:
        return True
    else:
        return False

random_numbers_for_pos = {
    6: (0xa66fe7dd, 0x1c),
    7: (0x357afcf8, 0x227),
    8: (0x00000015, 0x0),
    9: (0x5c156c54, 0x16c),
    10: (0xa66fe7dd, 0x1c),
    11: (0xe93ece66, 0x9d),
    12: (0x5c156c54, 0x16c),
    13: (0x5c156c54, 0x16c),
    14: (0xf3444241, 0x756),
    15: (0x4660a4c5, 0x1),
    16: (0xa66fe7dd, 0x1c),
}

printable_chars = [chr(i) for i in range(127)]

def get_char_for_pos(pos):
    start = "A"
    if pos in random_numbers_for_pos:
        for c in printable_chars:
            if eighth_unpack(c, random_numbers_for_pos[pos][0], random_numbers_for_pos[pos][1]):
                return c
        else:
            print('cannot solve eight_unpack for', pos)
    return chr(ord(start) + pos)


if __name__ == "__main__":
    flag_size = 0x21

    header = "\"flag{"
    end = "}\""

    content_len = flag_size - len(header) - len(end)
    content = [get_char_for_pos(i) for i in range(content_len)]

    print(header + ''.join(content) + end)

    