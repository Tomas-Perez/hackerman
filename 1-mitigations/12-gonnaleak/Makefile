.PHONY: gonnaleak
FLAG = -fno-pie -z execstack -no-pie

gonnaleak: gonnaleak.c
    gcc $(FLAG) -o $@ $<