# Validating the x18 behavior
1.  Run `make` to compile our code
2.  Run `./irq` to check whether the x18 register is cleared when an interrupt occurs.

# Expected results

After receiving 1000 interrupts, the program reports that each interrupt will clear the x18 register.

、、、
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
、、、
