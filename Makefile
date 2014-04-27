echod: epoll_echo.c
	gcc -g -O0 -Wall -o echod epoll_echo.c

utf8.so: lua-utf8.c
	gcc -fPIC --shared -g -O0 -Wall -I/usr/local/include -o $@ $^ -llua -L/usr/local/lib
	@lua test.lua

bitmap: bitmap.py
	python bitmap.py

clean:
	-rm echod
	-rm utf8.so

