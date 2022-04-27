# Basically c.py but it actually compiles to C and has no standard library.
import ast
from sys import argv
import os
def parse_args(x):
    return [f'{Compiler([arg.annotation]).compile()} {arg.arg}' for arg in x]


boilerplate = """// Generated by cpy - NO STD!
#define pydouble(x) (double)x
#define addr(x) &x

#define convert(type, ...) (type)__VA_ARGS__
#define arr_var(type, name, am, value) type name[am] = value

/* Start */
"""
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
            self.filename = f'{"/".join(temp)}'
        else:
            self.filename = f'{"/".join(temp)}.{ext}'

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
        fname = os.path.splitext(out)[0]+'.c'
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
                    end += f'"{value}"'
                elif isinstance(const.value, bool):
                    end += f'{str(const.value).lower()}'
                elif isinstance(const.value, float):
                    end += str(const.value)+'f'
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
                rest = target[1]
                iter_ = for_.iter

                if not isinstance(iter_, ast.Call):
                    self.errast("For loop must have a function.")
                    
                if not self.isocompile([iter_.func]) == 'range':
                    self.errast("For loop function must be range.")
                start = self.isocompile([iter_.args[0]])
                stop  = self.isocompile([iter_.args[1]])
                step  = self.isocompile([iter_.args[2]])
                
                end += f"for ({typ} {rest} = {start}; {rest} < {stop}; {rest} += {step}) {{\n{tab(self.isocompile(for_.body))}\n}}\n"

                
            elif self.inst(ast.AugAssign):
                var = self.peek()
                target = self.isocompile([var.target])
                end += f'{target} += {self.isocompile([var.value])};\n'

            elif self.inst(ast.BinOp):
                binop = self.peek()
                left = self.isocompile([binop.left])
                op = binop.op
                right = self.isocompile([binop.right])

                end += self.handleop(op, left, right)

            elif self.inst(ast.Name):
                end += self.peek().id

            elif self.inst(ast.Expr):
                expr = self.isocompile([self.peek().value])
                if isinstance(self.peek().value, ast.Call):
                    if self.isocompile([self.peek().value.func]) == '__cpp__':
                        end += f'{expr}\n'
                    else: end += f'{expr};\n'
                
                elif isinstance(self.peek().value, ast.Constant):
                    constant = self.peek().value.value
                    if isinstance(constant, str):
                        # end += f"/*{constant}*/"
                        pass
                    else: end += f'{expr};\n'
                else: end += f'{expr};\n'

            elif self.inst(ast.Call):
                fn = self.peek()
                name = self.isocompile([fn.func])
                args = [self.isocompile([x]) for x in fn.args]

                if name != 'py_entry_point':
                    if name == '__c__':
                        if [(x[0] == '"' and x[-1] == '"') or (x[0] == "'" and x[-1] == "'") for x in args] != [True] * len(args):
                            self.errast("__c__ only accepts string arguments")
                        inline = '\n'.join([x[1:-1] for x in args])
                        if inline.endswith(';'):
                            end += inline[:-1]
                        else: end += inline
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
                if name.startswith("cmacro_"):
                    args = ', '.join([self.isocompile([x]) for x in fn_def.args.args])
                    body = ' \\\n'.join(self.isocompile(fn_def.body).split('\n'))
                    end += f"#define {name}({args}) do {{ \\\n{tab(body)}\n}} while (false);\n"
                else:
                    args = parse_args(fn_def.args.args)
                    returns = self.isocompile([fn_def.returns])
                    if returns == '': returns = 'auto'
                    body = self.isocompile(fn_def.body)

                    end += f'{returns} {name}({", ".join(args)}) {{\n{tab(body)}\n}}\n'

            elif self.inst(ast.ClassDef):
                self.errast("cpy no std does not have classes.")

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
                op     = boolop.op
                left   = self.isocompile([boolop.values[0]])
                right  = self.isocompile([boolop.values[1]])

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
    print('usage: ./c-nostd.py <FILE>')
    quit(1)

file = argv[1]
compile_file(file)
