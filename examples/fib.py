def ppy__c__(x, *args): pass
ppy__c__("#include <stdio.h>")
def ppyprintf(x, *args): print(x % args, end='')

def fib(x: int) -> int:
    if x <= 1:return 1
    return fib(x-1)+fib(x-2)

def main() -> int:
    for int_i in range(1, 40, 1):
        ppyprintf("fib(%d) = %d\n", int_i, fib(int_i))

def py_entry_point(): main()

py_entry_point()