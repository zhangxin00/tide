# Define compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2

# Define targets and source files
TARGETS = irq

all: $(TARGETS)
irq: irq.c
	$(CC) $(CFLAGS) -o irq irq.c

# Clean up generated files
clean:
	rm -f $(TARGETS)

.PHONY: all clean

