.PHONY: server
FLAG =  -fno-stack-protector -fno-pie -z execstack -no-pie

server: server.c
    gcc $(FLAG) -o $@ $<