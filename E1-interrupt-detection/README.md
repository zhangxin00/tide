# Validating the x18 Behavior

## Setup and Execution

1. Compile the code:

   ```bash
   make
   ```

2. Run the test program:

   ```bash
   ./irq
   ```

## Expected Results

After receiving 1000 interrupts, the program should report that the `x18` register is cleared on every interrupt.

Example output:

```text
waiting for 1000 irqs
received 100 irqs
received 200 irqs
received 300 irqs
received 400 irqs
received 500 irqs
received 600 irqs
received 700 irqs
received 800 irqs
received 900 irqs
received 1000 irqs
TSC jumps (baseline that relies on a high-resolution timer): 1000
x18 cleared: 1000
```
