echod: epoll_echo.c
	gcc -g -O0 -Wall -o echod epoll_echo.c

bitmap: bitmap.py
	python bitmap.py

clean:
	-rm echod

