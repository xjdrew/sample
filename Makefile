echod: epoll_echo.c
	gcc -g -O0 -Wall -o echod epoll_echo.c
clean:
	-rm echod

