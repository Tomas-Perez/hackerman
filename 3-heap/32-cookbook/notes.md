# Interesting stuff

# Useless stuff (probably)

## main

sets an alarm for argv[1] seconds

## get_name

Reads the name with fgets. This means it stops at the first null terminator or \n.
Also, it will only read size - 1 characters, so the string will always be null-terminated.

# Ideas

- When adding a name to a new recipe the program is reading 0x40c bytes into the instructions buffer, this is way more than its size of aprox 0x380.

    We can overwrite the size of the top_chunk with this. At a certain fixed offset from the new recipe there is the top_chunk size. We have 140 bytes of overflow available.

    The same works when entering instructions for the new recipe.

    fgets is used to we have no leak possible here.

- The cookbook name is an arbitrary length and allocated on the heap. We can move the top_chunk by giving it the correct lenght.

- How to leak top_chunk address?
    
    Ingredients have a self pointer at the end, just after the name buffer. Manage to enter a name without a \0 and get a leak of the heap.

    What if we overflow the instructions buffer and allocate a new chunk AFTER? The allocation should overwrite the null terminator and get us to print everything after the string.

    **What worked:** exterminating all ingredients fills the tcache, when adding a new ingredient, malloc will give us a reused chunk from a bin. This means it will have a pointer to another chunk also in the bin. As an ingredient is allocated with malloc, this data is not erased and we get a leak to the heap on the "calories" field of the ingredient.

- How to leak libc?

    Once we have a leak of the top chunk and the size is whatever we want, we have an arbitrary write.

    Adding a name to the cookbook:
        Length: offset from current top chunk position to next place to write to
        Content: what to write at the current top chunk position




