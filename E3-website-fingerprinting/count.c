#include <mach/mach_time.h>
#include <mach/mach.h>
#include <stdio.h>
#include <stdint.h> 
#include <stdlib.h> 

#define T 10

void set_x18(int value) {
    __asm__ volatile("mov x0, %x0" : : "r"((uint64_t)value));
}

static int get_x18() {
    uint64_t value;
    __asm__ volatile("mov %x0, x0" : "=r"(value));
    return (int)value;
}

int main() {
    mach_timebase_info_data_t timebase_info;
    mach_timebase_info(&timebase_info);
    uint64_t numer = timebase_info.numer;
    uint64_t denom = timebase_info.denom;

    uint64_t *results = (uint64_t *)malloc(T * sizeof(uint64_t)); 
    if (results == NULL) {
        perror("Failed to allocate memory for results");
        return 1;
    }
    
    uint64_t count = 0;
    for (int i = 0; i < T; i++) {
        set_x18(20260424);
        while (get_x18() == 20260424) {
            count++;
        }
        results[i] = count;
        count = 0 ;
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
