# C.py
Incomplete Python to C++ Compiler

The compiler is very similiar to my other compiler, [Lua.py](https://github.com/Fxomt-III/Lua.py).

C.py has no lists, yet, BUT you can use the inline C++ ```__cpp__``` to create one.

C.py is a static programming language, not dynamic.

## Examples
```py
# Imports
import libc.no.iostream # #include <iostream>
import libc.h.iostream # #include <stdio.h>
import cpp.my_other_cpp_file # #include "my_other_cpp_file.cpp"

import cpp.my.file.in_.folders # #include "my/file/in_/folders.cpp"
```

there are also 'macros':
```py
def cppmacro_print(x):
    print(x)

#define cppmacro_print(x) do { \
    print(x); \
} while (false);
```

## Why not nuitka or Cython?
They compile fast, optimized, but unreadable C,
C.py compiles to fast, and readable C++.

for simple projects with no python dependencies,
you should use C.py, otherwise, use Nuitka/Cython/Etc.