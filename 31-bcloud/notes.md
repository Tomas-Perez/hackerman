# Interesting stuff

## byte_wise_read

Calls read reading a single byte "length" times until the given terminator is reached.
The terminator, or the last byte in the string is replaced by \0. However, if the input string is equal or longer than "length", the \0 will be in the "length" byte, outside of the buffer.

Inputting a string of the same size as the buffer will give us a non-terminated string inside the buffer. Anything that prints it will leak information.

## get_name

Zeroes out the local name buffer PLUS 16 more bytes.
Gets name from user with **byte_wise_read** (terminator \n).

Read bytes == size of local buffer.

Creates the global_name, a HEAP allocated string of size == size of local buffer.

Copies read name from local buffer to global_name with **strcpy**.
 
If we enter a name that is 64 bytes long, the local_name_buf will contain the 64 byte non-null terminated string. The null terminator will overflow local_name_buf by 1 byte.
strcpy at this time would just overflow the global_name by 1 byte with the null terminator.
However, after the local_name_buf there is a local variable, local_name_heap_ptr.
After the name is read into the local buffer, a malloc for global name is performed, and the address is stored in local_name_heap_ptr, overwriting the null-terminator.
**strcpy** now will write the following into global_name.
64 characters of user input for name + address to global_name (HEAP) // Null terminator is the initial byte of the canary.

The following call to welcome_message prints global_name, which will give us a leak to the address of global_name in the HEAP.

## sync_options

Zeroes out the local org buffer PLUS 80 more bytes.
Gets org from user using **byte_wise_read** (terminator \n), saves it in local_org.
Bytes to read == size of local_org.

Gets host from user using **byte_wise_read** (terminator \n), saves it in local_host.
Bytes to read < size of local_host.

Allocates 80 bytes to store the global_host. This is 12 bytes more than the local_host buffer. Stores it in local_host_heap_ptr.

Allocates 64 bytes to store global_org. Same size as local_org buffer. Stores it into global_org directly.

Copy local_host_heap_ptr into global_host.
Copy global_org into local_org_heap_ptr.

**strcpy** will copy the following into global_host (local_host_heap_ptr).
64 bytes of user input for host (local_host buffer is larger than input read, so null terminator is preserved).

After that, **strcpy** will copy the following into global_org (local_org_heap_ptr).
64 bytes of user input for org + address to global_org (HEAP) + 64 bytes of user input for host // Null terminator is the null terminator of reading host.
A total of 132 bytes, 68 bytes more than the global_org chunk.

Both global_org and global_host are only used in this function. It is pretty much useless to do anything here. 



## read_number
byte_wise_read of 16 bytes into a 20 byte buffer. No problem with null terminator here.
parses 16 bytes into an integer

## new_note
Checks that there are less than 10 notes loaded. Otherwise just prints a message.

The lenght of the note is set by the user through **read_number**. The note length will be the user given length + 4 bytes. 

Note content is user input through byte_wise_read, as the real note length has 4 bytes extra, there is no problem with the null terminator.

The note id is printed.

## edit_note
Note id is read with **read_number**. 
Checks if note id is between 0 and 9. Otherwise just prints a message.
Checks if note exists (not NULL). Otherwise just prints a message.
Note length is determined by the previous length, specified by new_note.
Note content is user input through byte_wise_read, as the real note length has 4 bytes extra, there is no problem with the null terminator.

## delete_note
Note id is read with **read_number**. 
Checks if note id is between 0 and 9. Otherwise just prints a message.
Checks if note exists (not NULL). Otherwise just prints a message.
Copies note address to local_note_ptr.
Sets global_notes[note_id] to NULL.
Sets global_notes_length[note_id] to 0.
Frees local_note_ptr.

# Useless stuff (probably)

## main
Does initial setup calling **setup_user**
Calls **get_option** and calls the selected option via a switch.
Infinite loop until **quit** is called. **quit** does not return, it is an exit.

## setup_user
**get_name**
**sync_options**

## get_option
read_number

## syn
Sets all synced_note flags to 1.

## quit
exit(0)

## show_note, invalid_option
Just a puts

# Ideas

PLT is code that calls the GOT.
GOT has the address to the function, but needs to be called from PLT (?).

With House of Force we can set the address to store a note to wherever we want.
This is done with the first note, note 0.
Set the address of the next note to the start of the global_notes buffer.

Note 1 will then be created with an address such that new allocations don't mess with our global_notes. Say 50.
With this note we can write the addresses of all the next notes, but no note except 0 and 1 have a size.
The size of note 0 is probably negative because of overflow, so it is useless.
Note 1 is the current note. We can write to global_notes[1] (what the program will see as the note 1 address) the address of the next note, note 2.
Create note 2 with a size of 4 (exact to avoid messing with other things).
NOW:
Editing note 1 will change the address of note 2, so whatever we put in the first 4 bytes of note 1 will be the address of note 2.
Editing note 2 will write to whatever address we set with note 1.

An arbitrary write is therefore:
    edit(note_1, where_to_write)
    edit(note_2, what_to_write)

- First replace free got with puts plt, now everything that would be freed is printed instead.
- Write to a note the address of puts got.
- Free the note, printing the puts got, which is an address in libc.
- Compute system with the offset from puts to system.
- Replace free got with address to system. Then, delete a note with the content "/bin/sh". This will call system("/bin/sh").

