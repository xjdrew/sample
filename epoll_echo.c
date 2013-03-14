#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <arpa/inet.h>


#define BACKLOG    5
#define MAX_EVENTS 10
#define BUFLEN     10
static int
do_use_fd(fd) {
    char buf[BUFLEN];
    int ret = 0;
    for(;;) {
        ssize_t len = read(fd, buf, BUFLEN-1);
        if(len > 0) {
            buf[len] = 0;
            if(write(fd, buf, len) != len) {
                ret = -1;
                break;
            }
            printf("[data %d] %s\n", fd, buf);
        } else {
            if(len == 0 || (errno != EAGAIN && errno != EWOULDBLOCK)) {
                ret = -1;
            }
            break;
        }
    }
    return ret;
}

static int 
setnonblocking(sockfd) {
    if(fcntl(sockfd, F_SETFL, O_NONBLOCK) == -1) {
        close(sockfd);
        return -1;
    }
    return 0;
}

static int
create_listen_socket(port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if(fd == -1) {
        perror("socket");
        return -1;
    }

    struct sockaddr_in listen_addr;
    listen_addr.sin_family = AF_INET;
    listen_addr.sin_port   = htons(port);
    listen_addr.sin_addr.s_addr   = INADDR_ANY;

    if(bind(fd, (struct sockaddr*)&listen_addr, sizeof(listen_addr)) == -1) {
        perror("bind");
        close(fd);
        return -1;
    }

    if(listen(fd, BACKLOG) == -1) {
        perror("listen");
        close(fd);
        return -1;
    }
    return fd;
}

int main(int argc, char** argv) {
    if(argc != 2) {
        printf("Usage: %s <listen port>\n", argv[0]);
        return 1;
    }
    
    unsigned short port = (unsigned short)atoi(argv[1]);
    int listen_sock = create_listen_socket(port);
    if (listen_sock == -1) {
        return 3;
    }

    int epollfd = epoll_create(MAX_EVENTS);
    if (epollfd == -1) {
        perror("epoll_create");
        return 4;
    }

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN;
    ev.data.fd = listen_sock;
    if (epoll_ctl(epollfd, EPOLL_CTL_ADD, listen_sock, &ev) == -1) {
        perror("epoll_ctl: listen_sock");
        return 5;
    }

    int nfds = 0;
    for(;;) {
        nfds = epoll_wait(epollfd, events, MAX_EVENTS, -1);
        if (nfds == -1) {
            perror("epoll_wait");
            return 6;
        }

        int n;
        for (n= 0; n < nfds; ++n) {
            if(events[n].data.fd == listen_sock) {
                struct sockaddr_in peer_addr;
                int addrlen = sizeof(peer_addr);
                int conn_sock = accept(listen_sock, (struct sockaddr*)&peer_addr, (socklen_t*)&addrlen);
                if(conn_sock == -1) {
                    perror("accept");
                    return 7;
                }

                printf("[accept] addr: %s, port: %hu, fd: %d\n", inet_ntoa(peer_addr.sin_addr), ntohs(peer_addr.sin_port), conn_sock); 
                if(setnonblocking(conn_sock) == 0) {
                    ev.events = EPOLLIN | EPOLLET;
                    ev.data.fd = conn_sock;
                    if(epoll_ctl(epollfd, EPOLL_CTL_ADD, conn_sock, &ev) == -1) {
                        perror("epoll_ctl: conn_sock");
                        close(conn_sock);
                    }
                }
            } else {
                if(do_use_fd(events[n].data.fd) == -1) {
                    epoll_ctl(epollfd, EPOLL_CTL_DEL, events[n].data.fd, NULL);
                    close(events[n].data.fd);
                    printf("[close %d]\n", events[n].data.fd);
                }
            }
        }
    }

    return 0;
}

