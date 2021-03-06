# c.py is now merged with c-nostd.py,
# so it generates both C and C++ code
import ast
from sys import argv
import os


def parse_args(x):
    return [f'{Compiler([arg.annotation]).compile()} {arg.arg}' for arg in x]


boilerplate = """// Generated by cpy
#define pydouble(x) (double)x
#define convert(type, ...) (type)__VA_ARGS__
#define arr_var(type, name, am, ...) type name[am] = __VA_ARGS__
#define pyunsigned(x) unsigned x
#define arr(type, name, sz) type name[sz]
#define pyconst(x) const x
#define arrow(x, y) x->y

typedef char* strarr[];
typedef char* str;
/* Start */
"""


def parse_name(x):
    out = []
    for i in x:
        if i == 'outc':
            out.append('..')
        else:
            out.append(i)
    return out

#  import [libc].<ext no | any>.<filename>


class Module:
    def __init__(self, mod):
        self.mod = mod
        temp = mod.split('.')
        out = False
        if temp[0] == 'libc':
            out = True
            temp = temp[1:]

        ext = temp[0]
        temp = temp[1:]

        if ext == 'no':
            self.filename = f'{"/".join(parse_name(temp))}'
        else:
            self.filename = f'{"/".join(parse_name(temp))}.{ext}'

        self.b1 = '<' if out else '"'
        self.b2 = '>' if out else '"'

    def view(self):
        return f"#include {self.b1}{self.filename}{self.b2}\n"


class CFile:
    def __init__(self):
        self.out = ''

    def append(self, x):
        self.out += x

    def write(self, out):
        x = os.path.splitext(out)
        fname = x[0]+'.c'
        if x[1] == '.hpy':
            fname = x[0]+'.h'

        with open(fname, 'w') as f:
            f.write(self.strip_excess())

    def strip_excess(self):
        return self.out.rstrip()


def tab(x): return '\n'.join(['    ' + y for y in x.split('\n')]).rstrip()


variables = {}


class Compiler:
    def __init__(self, pyast):
        self.pos = 0
        self.ast = pyast
        self.cfile = CFile()
        self.cfile.append(boilerplate)

    def errast(self, node, msg):
        print(f'[compiler {node.lineno}:{node.col_offset}]: {msg}')

    def extract(self, if_stmt, elseifs, else_):
        for i in if_stmt.orelse:
            if isinstance(i, ast.If):
                test = self.isocompile([i.test])
                elbody = self.isocompile(i.body)
                elseifs.append([test, elbody])
                if i.orelse != []:
                    self.extract(i, elseifs, else_)
            else:
                else_.append(self.isocompile(if_stmt.orelse))
                return

    def handleop(self, x, y, z):
        if isinstance(x, ast.Add):
            return f'{y} + {z}'
        elif isinstance(x, ast.Sub):
            return f'{y} - {z}'
        elif isinstance(x, ast.Mult):
            return f'{y} * {z}'
        elif isinstance(x, ast.Div):
            return f'{y} / {z}'
        elif isinstance(x, ast.Mod):
            return f'{y} % {z}'
        elif isinstance(x, ast.LShift):
            return f'{y} << {z}'
        elif isinstance(x, ast.RShift):
            return f'{y} >> {z}'
        print(f'[error]: unknown operator {x}')
        quit(1)

    def cmp(self, x, y, z):
        op = ''
        if isinstance(x, ast.Eq):
            op = '=='
        elif isinstance(x, ast.NotEq):
            op = '!='
        elif isinstance(x, ast.Gt):
            op = '>'
        elif isinstance(x, ast.GtE):
            op = '>='
        elif isinstance(x, ast.Lt):
            op = '<'
        elif isinstance(x, ast.LtE):
            op = '<='

        if op != '':
            return f'{y} {op} {z}'
        else:
            print(f'[error]: unknown CMP-operator {x}')
            quit(1)

    def compile(self):
        end = ''

        while not self.at_end():
            if self.inst(ast.AnnAssign):
                var_ = self.peek()
                name = self.isocompile([var_.target])
                typ = self.isocompile([var_.annotation])
                if var_.value:
                    end += f'{typ} {name} = {self.isocompile([var_.value])};\n'
                else:
                    end += f'{typ} {name};\n'

            elif self.inst(ast.Assign):
                var_ = self.peek()
                name = self.isocompile([var_.targets[0]])
                end += f'{name} = {self.isocompile([var_.value])};\n'

            elif self.inst(ast.Constant):
                const = self.peek()
                if isinstance(const.value, str):
                    value = const.value \
                        .replace("\n", "\\n") \
                        .replace("\r", "\\r")
                    if const.kind == 'u':
                        end += f"'{value}'"
                    else: end += f'"{value}"'
                elif isinstance(const.value, bool):
                    end += f'{str(const.value).lower()}'
                elif isinstance(const.value, float):
                    end += str(const.value)+'f'
                elif isinstance(const.value, None):
                    end += "NULL"
                else:
                    end += str(const.value)

            elif self.inst(ast.Dict):
                pass

            elif self.inst(ast.Subscript):
                sub = self.peek()
                value = self.isocompile([sub.value])
                slice = self.isocompile([sub.slice])
                end += f'{value}[{slice}]'

            elif self.inst(ast.For):
                for_ = self.peek()
                target = for_.target.id.split('_', 1)
                typ = target[0]
                try:
                    rest = target[1]
                except:
                    self.errast(for_, f"Must have name after type '{typ}'.")
                    quit(1)
                iter_ = for_.iter
                isrange = False

                if isinstance(iter_, ast.Call):
                    if self.isocompile([iter_.func]) == 'range':
                        isrange = True

                if isrange:
                    start = self.isocompile([iter_.args[0]])
                    stop = self.isocompile([iter_.args[1]])
                    step = self.isocompile([iter_.args[2]])

                    end += f"for ({typ} {typ}_{rest} = {start}; {typ}_{rest} < {stop}; {typ}_{rest} += {step}) {{\n{tab(self.isocompile(for_.body))}\n}}\n"
                else:
                    end += f"for ({typ} {typ}_{rest} : {self.isocompile([iter_])}) {{\n{tab(self.isocompile(for_.body))}\n}}\n"

            elif self.inst(ast.AugAssign):
                var = self.peek()
                target = self.isocompile([var.target])
                end += f'{target} += {self.isocompile([var.value])};\n'

            elif self.inst(ast.BinOp):
                binop = self.peek()
                left = self.isocompile([binop.left])
                if isinstance(binop.left, ast.BinOp):
                    left = f'({left})'

                op = binop.op
                right = self.isocompile([binop.right])
                print(binop.right)
                end += self.handleop(op, left, right)

            elif self.inst(ast.Name):
                id = self.peek().id
                if id.startswith("cptr_"):
                    id = id.split("cptr_")[1]
                    end += f'*{id}'
                if id.startswith("caddr_"):
                    id = id.split("caddr_")[1]
                    end += f'&{id}'
                else:
                    end += id
            elif self.inst(ast.Expr):
                expr = self.isocompile([self.peek().value])
                if isinstance(self.peek().value, ast.Call):
                    name = self.isocompile([self.peek().value.func])
                    if name == '__c__':
                        end += f'{expr}\n'
                    elif name == 'nosemi':
                        arg = self.isocompile([self.peek().value.args[0]])
                        end += f'{arg}\n'
                    else:
                        end += f'{expr};\n'
                elif isinstance(self.peek().value, ast.Constant):
                    constant = self.peek().value.value
                    if isinstance(constant, str):
                        # end += f"/*{constant}*/"
                        pass
                    else:
                        end += f'{expr};\n'
                else:
                    end += f'{expr};\n'

            elif self.inst(ast.Call):
                fn = self.peek()
                name = self.isocompile([fn.func])
                if name.startswith('ppy'):
                    name = name.split('ppy')[1]
                args = [self.isocompile([x]) for x in fn.args]

                if name != 'py_entry_point':
                    if name == '__c__':
                        if [(x[0] == '"' and x[-1] == '"') or (x[0] == "'" and x[-1] == "'") for x in args] != [True] * len(args):
                            self.errast(
                                fn, "__c__ only accepts string arguments")
                        inline = '\n'.join([x[1:-1] for x in args])
                        end += inline
                    else:
                        end += f'{name}({", ".join(args)})'
            elif self.inst(ast.While):
                while_ = self.peek()
                test = self.isocompile([while_.test])
                body = self.isocompile(while_.body)
                end += f"while ({test}) {{\n{tab(body)}\n}}\n"

            elif self.inst(ast.Return):
                end += f'return {self.isocompile([self.peek().value])};\n'

            elif self.inst(ast.Attribute):
                attr = self.peek()
                name = self.isocompile([attr.value])
                end += f'{name}.{attr.attr}'

            elif self.inst(ast.Import):
                import_ = self.peek()
                if not import_.names[0].name.startswith('pystub_'):
                    name = Module(import_.names[0].name)
                    end += name.view()

            elif self.inst(ast.Compare):
                cmp = self.peek()
                left = self.isocompile([cmp.left])
                right = self.isocompile([cmp.comparators[0]])
                op = self.cmp(cmp.ops[0], left, right)
                end += op

            elif self.inst(ast.List):
                lst = self.peek()
                elts = ', '.join(self.isocompile([x]) for x in lst.elts)

                end += f"{{{elts}}}"
            elif self.inst(ast.If):
                If = self.peek()
                test = self.isocompile([If.test])
                body = self.isocompile(If.body)
                elseifs = []
                else_ = []
                self.extract(If, elseifs, else_)
                end += f'if ({test}) {{\n{tab(body)}\n}} '
                for eif in elseifs:
                    end += f'else if ({eif[0]}) {{\n{tab(eif[1])}\n}} '
                if len(else_) > 0:
                    end += f'else {{\n{tab(else_[0])}\n}}'
                end += '\n'

            elif self.inst(ast.FunctionDef):
                fn_def = self.peek()
                name = fn_def.name
                # Port python
                if not name.startswith("ppy") and name != 'py_entry_point':
                    if name.startswith("cmacro_"):
                        args = '('+', '.join([self.isocompile([x])
                                              for x in fn_def.args.args])+')'
                        if len(fn_def.args.args) == 0:
                            args = ''
                        body = ' \n'.join(self.isocompile(
                            fn_def.body).split('\n'))
                        name = name.split('cmacro_')[1]
                        if len(fn_def.body) > 1:
                            end += f"#define {name}{args} do {{ \\\n{tab(body)}\n}} while (false);\n"
                        else:
                            end += f"#define {name}{args} {body}\n"
                    else:
                        args = parse_args(fn_def.args.args)
                        returns = self.isocompile([fn_def.returns])
                        if returns == '':
                            returns = 'auto'
                        body = self.isocompile(fn_def.body)

                        if body.strip() == "":
                            end += f'{returns} {name}({", ".join(args)});\n'
                        else:
                            end += f'{returns} {name}({", ".join(args)}) {{\n{tab(body)}\n}}\n'

            elif self.inst(ast.ClassDef):
                klass = self.peek()
                name = klass.name     
                end += f"class {name} {{\npublic:\n{tab(self.isocompile(klass.body))}\n}};\n"

            elif self.inst(ast.UnaryOp):
                un = self.peek()
                op = un.op
                value = self.isocompile([un.operand])
                if isinstance(op, ast.USub):
                    end += f'-{value}'
                if isinstance(op, ast.Not):
                    end += f'!{value}'

            elif self.inst(ast.BoolOp):
                boolop = self.peek()
                op = boolop.op
                left = self.isocompile([boolop.values[0]])
                right = self.isocompile([boolop.values[1]])

                if isinstance(op, ast.Or):
                    end += f'{left} || {right}'
                elif isinstance(op, ast.And):
                    end += f'{left} && {right}'
            self.advance()

        return end
    # ----------
    # | Utils  |
    # ----------

    def isocompile(self, *args):
        return Compiler(*args).compile()

    def inst(self, x):
        return isinstance(self.peek(), x)

    def advance(self):
        self.pos += 1

    def at_end(self):
        return self.pos >= len(self.ast)

    def devance(self):
        self.pos -= 1

    def add(self, item):
        self.cfile.append(item)

    def write(self, fname):
        self.cfile.write(fname)

    def peek(self):
        return self.ast[self.pos]

    def prev(self):
        return self.ast[self.pos-1]


def gen_ast(x):
    tree = ast.parse(open(x).read())
    return tree.body


def compile_file(x):
    compiler = Compiler(gen_ast(x))
    compiler.add(compiler.compile())
    compiler.write(x)


if len(argv) <= 1:
    print('usage: cpy <FILE>')
    quit(1)

file = argv[1]
compile_file(file)
