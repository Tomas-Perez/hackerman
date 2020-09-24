#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netinet/in.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

char buffer[0x1000];

void get_name(int fd, char *local_buf){
  printf("What is your name?\\n");
  read(fd, buffer, 0x1000);
  memcpy(local_buf, buffer, 0x1000);
}

void prog(int fd){
  char local_buf[1000];
  get_name(fd, local_buf);
  write(fd, "Hello Mr.", 9); 
  write(fd, local_buf, strlen(local_buf));
  write(fd, "\n", 1);
}

int main()
{
    int server_sockfd, client_sockfd;
    int server_len, client_len;
    struct sockaddr_in server_address;
    struct sockaddr_in client_address;

    server_sockfd = socket(AF_INET, SOCK_STREAM, 0);

    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = htonl(INADDR_ANY);
    server_address.sin_port = htons(2005);
    server_len = sizeof(server_address);
    bind(server_sockfd, (struct sockaddr *)&server_address,server_len);

    /* Create a connection queue, ignore child exit details and wait for
    clients. */

    listen(server_sockfd, 5);

    signal(SIGCHLD, SIG_IGN);

    while(1) {
        printf("server waiting\n");

        /* Accept connection. */

        client_len = sizeof(client_address);
        client_sockfd = accept(server_sockfd,(struct sockaddr *)&client_address, &client_len);

        /* Fork to create a process for this client and perform a test to see
        whether we're the parent or the child. */

        if(fork() == 0) {

            /* If we're the child, we can now read/write to the client on
            client_sockfd. */
            write(client_sockfd,"  _________                                \n /   _____/ ______________  __ ___________ \n \\_____  \\_/ __ \\_  __ \\  \\/ // __ \\_  __ \\\n /        \\  ___/|  | \\/\\   /\\  ___/|  | \\/\n/_______  /\\___  >__|    \\_/  \\___  >__|   \n        \\/     \\/                 \\/       \n\n\n", 266);
            prog(client_sockfd);
            close(client_sockfd);
            exit(0);
        }

        /* Otherwise, we must be the parent and our work for this client is
        finished. */

        else {
            close(client_sockfd);
        }
    }
}