import ast
import sympy
import astunparse


def simple_parse(tree):
    res = []
    for node in ast.iter_child_nodes(tree):
        if type(node) == ast.Assign:
            targets = astunparse.unparse(node.targets).replace('\n', ' = ')
            exp = sympy.pretty(sympy.sympify(astunparse.unparse(node.value)))
            parts = exp.split('\n')
            if len(parts) != 1:
                parts[1] = targets + parts[1]
                for i in range(len(parts)):
                    if i != 1:
                        parts[i] = ' ' * len(targets) + parts[i]
            else:
                parts[0] = targets + parts[0]
            res.append('\n'.join(parts))
    return res


tree = ast.parse('a = 12/x/z/y/(255*hh+qwert)\nb = 12*z')
res = simple_parse(tree)
for expr in res:
    print(expr)
