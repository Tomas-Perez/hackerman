x86 shellcode from Computer Security

```asm
1.      jmp     end
2.      start:
3.      pop     esi
4.      mov     DWORD PTR [esi+0x8], esi
5.      xor     eax, eax
6.      mov     BYTE PTR [esi+0x7], al
7.      mov     DWORD PTR [esi+0xc], eax
8.      mov     al, 0xb
9.      mov     ebx, esi
10.     lea     ecx, [esi + 0x8]
11.     lea     edx, [esi + 0xc]
12.     int     0x80
13.     end:
14.     call    start 
15.     .string "/bin/sh"
```

Execution:

1.  L1 - Jump to the _end_ label
2. L14 - Call the _start_ label, this will push the **eip** on the stack, saving the address of line 15 (location of "/bin/sh")
3. L3 - Pop the top of the stack (address of "/bin/sh") onto the **esi** register.
4. L4 - Store the contents of **esi** on the address in memory **esi**+0x8 (that is 8 bytes after the start of "/bin/sh")
    A proper "/bin/sh" string is 8 bytes long, 7 characters plus the null terminator.
    So the address pointing to the start of the "/bin/sh" string will be just after the end of the proper string.
5. L5 - Zero out the **eax** register
6. L6 - Store the contents of **al** (lower byte of **eax**, so 0x00) on **esi**+0x7, this sets the null terminator for the "/bin/sh" string.
    We cannot be sure that the "/bin/sh" string was properly null terminated so we make sure to set the last byte to 0x00.
7. L7 - Store the contents of **eax** (0x00000000) to the address **esi**+0xc, that is exactly at the end of the of the pointer to "/bin/sh" we saved in line 4.
8. L8 - Move 0xb to **al** (lower byte of **eax**). Now **eax** = 0x0000000b
9. L9 - Move **esi** to **ebx**. **ebx** now contains a pointer to a proper "/bin/sh" string. So **ebx** = "/bin/sh"
10. L10 - Move the address **esi**+0x8 to **ecx**. **ecx** now contains a pointer to a pointer to "/bin/sh", the next pointer over (**esi**+0c) is NULL. So ***exc** = { "/bin/sh", NULL }
11. L11 - Move the address **esi**+0xc to **edx**. **edx** now contains a pointer to a null pointer. So ***edx** = { NULL }.
12. L12 - Perform a syscall.
    **eax** = 0xb. The syscall to perform is *execve*
    execve(const char *name (**ebx**), const char *const *argv (**ecx**), const char *const *envp (**edx**))
    **ebx** = "/bin/sh"
    ***exc** = { "/bin/sh", NULL }
    ***edx** = { NULL }

