import ast
import astunparse

pow_sign = '⋅'
div_sign = '/'


def parse_expr(node):
    if type(node) == ast.Assign:
        expr = parse_expr(node.value)
        targets = astunparse.unparse(node.targets).replace('\n', '=')
        return f'{targets}{expr}'
    elif type(node) == ast.BinOp:
        left = parse_expr(node.left)
        right = parse_expr(node.right)
        if type(node.op) == ast.Mult:
            return left + pow_sign + right
        elif type(node.op) == ast.Div:
            return left + div_sign + right
    elif type(node) == ast.Name:
        return str(node.id)
    elif type(node) == ast.Constant:
        return str(node.value)


def main_parse(module):
    res = []
    for node in ast.iter_child_nodes(module):
        res.append(parse_expr(node))
    return res


tree = ast.parse('a=x*z/2*z\nb = 12*z\n')
res = main_parse(tree)
for epr in res:
    print(epr)
