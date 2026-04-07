# Define compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2

# Define targets and source files
TARGETS = tide

all: $(TARGETS)

count: count.c
	$(CC) $(CFLAGS) -o tide tide.c

# Clean up generated files
clean:
	rm -f $(TARGETS)

.PHONY: all clean

