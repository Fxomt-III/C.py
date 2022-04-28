# C.py
Note: c.py and c-nostd.py have merged, to use print statements, you need to import it manually.

Incomplete Python to C/++ Compiler

The compiler is very similiar to my other compiler, [Lua.py](https://github.com/Fxomt-III/Lua.py) (note: lua.py has been discontinued).

C.py is a static programming language, not dynamic.

## Tutorial
### Imports
in cpy (Will be calling it cpy for the rest of the tutorial), things work differently,
imports are in this format:
```python
import [libc.] <ext>.<directory with .'s as /'s.>
#      ------  ----- ----------------------------
```
libc means if it is out of the directory,
basically, if libc: use <>, else: use "".
```
import libc.h.stdio # <stdio.h>
import h.stdio # "stdio.h"
```
ext is the extension of the file, there is a special extension for importing C++ files,
the 'no' extension, it means it has no extension.
```python
import libc.no.iostream # <iostream>
import libc.hpp.iostream # <iostream.hpp>
```

the last is obvious.
### Inline C/++
To use inline C/++, use the \_\_c\_\_.
### For loops
```python
for int_i in list_:
    do_something(int_i)
```
due to python limitations for not being able to specify types for for loop variables,
you have to create a for loop variable with < type >_ in the beginning
```python
# In range, you have to specify all of the arguments.
for int_i in range(0, 10, 1):
    do_something(int_i)
```
### Variables
variables are like this:
```python
var: int = 123
```
### Functions
```python
def main() -> int:
    pass

def func_that_returns_auto(): # if you did not specify the type, it will default to 'auto'.
    pass
```

### Lists
```python
# int myarr[3] = {0, 1, 2, 3};
arr_var(int, myarr, 3, [0, 1, 2, 3])
```

### Conversion
```python
# (int)0.1f
convert(int, 0.1)
```

### Doubles
```python
# 0.1f -> (double)0.1f
pydouble(0.1)
```

### Macros
for no-std use cmacro_, else, use cppmacro.
you should use this if you want 'python style' macros,
if you want C/++ macros, use inline C/++.
```python
def cmacro_printf(x):
    show_characters(x) # -> #define cmacro_printf(x) do { \ 
#                               show_characters(x) \
#                           } while (false);
__c__("#define printf(x) show_characters(x);")
```
If you want to ccreate macros like this:
```cpp
#define dead_beef 0xDEADBEEF
```
you use this:
```python
def cmacro_dead_beef(): nosemi(0xDEADBEEF)
#define dead_beef 3735928559
```
if you did not specify nosemi, it will compile to:
```cpp
#define dead_beef 3735928559;
```

### 'Stubs'
sometimes you want to use a C library, (my_cool_lib.h), but the editor complains that it does not exist,
to fix this, you use ```from <STUB_NAME> import *```, stub_name can be anything.

```cpp
// my_cool_lib.h
void do_something(int x) {
    printf("%d", x);
}
int mycoolvar = 123;
```
```py
# port of my_cool_lib.h
def do_something(x): pass
mycoolvar = None
```
```py
#my_cool_cpy_file.py
from port_mcl import * # CPY will ignore this and will not compile this
import h.my_cool_lib

do_something(mycoolvar)
```
now it will not complain!

### py_entry_point
Say you want to make a program that will work on C/++ AND python,
for this you use py_entry_point:
```python
def fib(x):
    if x <= 0:
        return 1
    return fib(x - 1) + fib(x - 2)

def main(): # C/++ Entry point
    print("%d", fib(7))

def py_entry_point(): # Python entry point
    main() # You can also call the C/++ entry point, since it is a normal python function

py_entry_point() # Do not forget to call this, cpy will ignore this, but python will not.
```
### Types
str             -> char*
int             -> int
float           -> float
pydouble(x)     -> double
pyunsigned(str) -> unsigned char*
pyunsigned(int) -> unsigned int

### Math
cpy's way of compiling math is weird, say we had this operation:
```py
x: int = 2*(80)*(25)-2
```
It will compile to this:
```c
int x = ((2 * 80) * 25) - 2;
```
Atleast it works!
### ppy
say we wanted to make a program that works in both C/++ And python,
and we wanted to use strlen, but python only has len, and if
we try to make a function named strlen, it will override the C
strlen, to fix this, we use ppy, which is basically an alias for C functions:
```python
# cpy will ignore this, therefore not overriding the c strlen.
def ppystrlen(x): return len(x) 
def main() -> int:
    return ppystrlen("Hello")
```

this will compile to:
```cpp
int main() {
    return strlen("Hello");
}
```
### Char type
python has no chartype, to fix this, unicode strings are treated as chartypes:
```py
putchar(u"A")
# C: putchar('A');
```
### Unsigned types
```python
var: pyunsigned(int) = 123
```