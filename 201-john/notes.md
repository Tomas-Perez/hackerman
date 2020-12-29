All relevant functions except for what's needed to unpack the binary and repack it are packed.
Main starts the program by calling **unpack** at the address of the first function.

**unpack**: unpacks a function, calls it and then repacks it again
- arg[0]: address to the start of the packed function
- arg[1]: length of the function

**repack**: repacks a function
- arg[0]: address to the start of the unpacked function
- arg[1]: length of the function

The unpacked assembly can be dumped at the time when a function is called in the **unpack** function or when **repack** is called.