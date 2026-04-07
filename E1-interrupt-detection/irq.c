#include <mach/mach_time.h>
#include <stdio.h>

#define THRESHOLD 5000

void set_x18(int value) {
    __asm__ volatile("mov x18, %x0" : : "r"((uint64_t)value));
}

int get_x18() {
    uint64_t value;
    __asm__ volatile("mov %x0, x18" : "=r"(value));
    return (int)value;
}

int main() {
    mach_timebase_info_data_t info;
    mach_timebase_info(&info);

    uint64_t start, end, diff;
    int count_zero = 0;
    int sum = 0;

    set_x18(1024);
    printf("waiting for 1000 irqs\n");

    while (1) {
        start = mach_absolute_time();
        end = mach_absolute_time();
        diff = (end - start) * info.numer / info.denom;

        if (diff > 1000) {
            sum++;
            if (get_x18()==0) {
                count_zero++;
            }
            set_x18(1024);
	    if(sum%100==0){
		printf("received %d irqs\n", sum);
}
            if(sum==1000)
                break;
        }
    }

    printf("TSC jumps (baseline that relies on a high-resolution timer): %d\nx18 cleared: %d\n", sum, count_zero);

    return 0;
}
