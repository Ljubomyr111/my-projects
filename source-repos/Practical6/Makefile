CC = gcc
CFLAGS = -Iinclude -Wall -Wextra -std=c99
SRC = src/array_utils.c

.PHONY: all demo tests clean

all: demo tests

demo: demo/demo.c $(SRC)
	$(CC) $(CFLAGS) demo/demo.c $(SRC) -o demo/demo

tests: tests/tests.c $(SRC)
	$(CC) $(CFLAGS) tests/tests.c $(SRC) -o tests/tests

clean:
	rm -f demo/demo tests/tests
