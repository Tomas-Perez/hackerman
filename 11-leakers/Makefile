.PHONY: leakers
FLAG = -fno-pie -z execstack -no-pie

leakers: leakers.c
    gcc $(FLAG) -o $@ $<