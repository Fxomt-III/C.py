def ppy__c__(*args): pass
def ppyconvert(x, y): return x(y)
def ppyprintf(x, *args): print(x % args, end='')
def ppyputchar(x): print(x, end='')
def ppystrlen(x): return len(x)

ppy__c__("#include <stdio.h>")
ppy__c__("#include <string.h>")

def main() -> int:
    chars: str = "..*-=:;#$"
    max_iter: int = 32
    for int_x in range(-32, 32, 1):
        for int_y in range(-80, 80, 1):
            cR: float = ppyconvert(float, int_y/32)
            cI: float = ppyconvert(float, int_x/16)
            
            
            x2: float = 0
            y2: float = 0
            
            iter: int = 0
            
            while x2 * x2 + y2 * y2 <= 4 and iter < max_iter:
                temp: float = x2 * x2 - y2 * y2 + cR
                y2 = 2 *x2 * y2 + cI
                x2 = temp
                iter += 1
            if iter < max_iter:
                ppyprintf("%c", chars[iter % ppystrlen(chars)])
            else:
                ppyprintf(" ")
        ppyputchar(u'\n')

def py_entry_point():
    main()

py_entry_point()
