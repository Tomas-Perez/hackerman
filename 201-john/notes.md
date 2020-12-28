Unpack function creates a page where the code can write and execute the unpack code.
This page starts at 0x8049000 and goes up to 0x804a000.

unpack(start of code, code_length)
Unpacks the code, executes it and unpacks it again before returning.

First call: unpack(0x0804970e, 0x53)
    Unpacks code from 0x0804970e to 0x0804985a

Second call: unpack(0x80492a0, 0x11)
    Unpacks code from 0x80492a0 to 0x080492b1