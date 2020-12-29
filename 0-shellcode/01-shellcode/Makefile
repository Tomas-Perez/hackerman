.PHONY: shellcode
FLAG =  -fno-stack-protector -fno-pie -z execstack -no-pie

shellcode: shellcode.c
    gcc $(FLAG) -o $@ $<