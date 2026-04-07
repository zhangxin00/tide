#include <mach/mach_time.h>
#include <mach/mach.h>
#include <stdio.h>
#include <stdint.h> 
#include <stdlib.h> 

#define T 5000

void set_x18(int value) {
    __asm__ volatile("mov x18, %x0" : : "r"((uint64_t)value));
}

static int get_x18() {
    uint64_t value;
    __asm__ volatile("mov %x0, x18" : "=r"(value));
    return (int)value;
}

int count_tick()
{
	int count=0;
    printf("set_x18\n");

	set_x18(1);

	while (get_x18() ==1)
	{
		count++;
	}
    printf("caught one interrupt\n");
	return count;
}

int main() {
    uint64_t *results = (uint64_t *)malloc(T * sizeof(uint64_t)); 
    if (results == NULL) {
        perror("Failed to allocate memory for results");
        return 1;
    }

    uint64_t count = 0;
    
    for (int i = 0; i < T; i++) {
        set_x18(1);
        while (get_x18() != 0) {
            count++;
        }
        results[i] = count;
        count = 0;
    }

    FILE *file = fopen("./count.txt", "w");
    if (file == NULL) {
        perror("Failed to open file");
        free(results); 
        return 1;
    }

    for (int i = 0; i < T; i++) {
        fprintf(file, "%llu\n", results[i]);
    }
    fclose(file); 
    free(results); 

    return 0;
}
