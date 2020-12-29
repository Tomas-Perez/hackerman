.PHONY: gimme3bytes
FLAG = -fno-stack-protector -fno-pie -z execstack -no-pie

gimme3bytes: gimme3bytes.c
    gcc $(FLAG) -o $@ $<