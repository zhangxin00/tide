# Define compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2

# Define targets and source files
TARGETS = sender receiver

all: $(TARGETS)
sender: sender.c
	$(CC) $(CFLAGS) -o sender sender.c
receiver: receiver.c
	$(CC) $(CFLAGS) -o receiver receiver.c
# Clean up generated files
clean:
	rm -f $(TARGETS)
	rm -f $(TARGETS)

.PHONY: all clean

