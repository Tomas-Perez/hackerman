import math

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

random_numbers_for_pos = [
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

def get_char_for_pos(pos):
    start = "A"
    if pos in range(6, 17):
        for c in printable_chars:
            if eighth_unpack(c, random_numbers_for_pos[pos - 6]):
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

    