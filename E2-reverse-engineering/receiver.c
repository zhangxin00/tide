#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/time.h>

#define RUN_TIME_MS 10000

// 以下两个函数用于操作 x18 寄存器
static void set_x18(int value) {
    __asm__ volatile("mov x18, %x0" : : "r"((uint64_t)value));
}

static int get_x18() {
    uint64_t value;
    __asm__ volatile("mov %x0, x18" : "=r"(value));
    return (int)value;
}

int main(int argc, char *argv[]) {
    int core = -1;
    if (argc >= 2) {
        core = atoi(argv[1]);
    }

    uint64_t count = 0;
    uint64_t junk = 0;
    int sum_count = 0;

    struct timeval start, end;
    uint64_t elapsed_time = 0;

    gettimeofday(&start, NULL);

    while (elapsed_time < RUN_TIME_MS) {
        set_x18(1);
        while (get_x18() != 0) {
            junk++;
        }

        count++;
        sum_count++;

        gettimeofday(&end, NULL);
        elapsed_time = (end.tv_sec - start.tv_sec) * 1000000ULL +
                       (end.tv_usec - start.tv_usec);
        elapsed_time /= 1000;
    }

    printf("sum count is %d\n", sum_count);

    system("mkdir -p ./rec");

    char filename[256];
    if (core >= 0) {
        snprintf(filename, sizeof(filename), "./rec/receiver_%d.txt", core);
    } else {
        snprintf(filename, sizeof(filename), "./rec/receiver.txt");
    }

    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("receiver: Failed to open file");
        return 1;
    }

    fprintf(file, "%llu\n", (unsigned long long)count);
    fclose(file);

    return 0;
}
