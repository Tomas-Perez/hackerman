.PHONY: onlyreadwrite
FLAG =  -fno-stack-protector -fno-pie -z execstack -no-pie

onlyreadwrite: onlyreadwrite.c
    gcc $(FLAG) -o $@ $<