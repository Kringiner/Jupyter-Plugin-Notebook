import ast
import json
import sys
from abc import ABC

import astunparse
from notebook.base.handlers import IPythonHandler

mathml = '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">'
equal_sign = '&#x0003D;'
pow_sign = '&#x22C5;'
plus_sign = '&#x0002B;'
minus_sign = '&#x02212;'
left_bracket = '<mo stretchy="true" fence="true" form="prefix">&#x00028;</mo>'
right_bracket = '<mo stretchy="true" fence="true" form="postfix">&#x00029;</mo>'

priorities = {ast.Div: 2, ast.Mult: 2, ast.Sub: 1, ast.Add: 1, ast.BinOp: sys.maxsize}
math_names = {'alpha': '&#x03B1;', 'beta': '&#x03B2;'}


class PrettyPythonHandler(IPythonHandler, ABC):
    def post(self):
        python_code = self.get_json_body()['code']
        latex_code = module_parser(ast.parse(python_code))
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        latex_res = {'latex_code': latex_code}
        self.write(json.dumps(latex_res))


def parse_expr(node) -> str:
    if type(node) == ast.Import:
        import_expr = ast.unparse(node).split()
        import_keyword = import_expr[0]
        module_name = import_expr[1]
        return f'{mathml}<mrow><mtext><mo class="keyword">{import_keyword}</mo> {module_name}</mtext></mrow></math>'
    elif type(node) == ast.ImportFrom:
        import_expr = ast.unparse(node).split()
        from_keyword = import_expr[0]
        module_name = import_expr[1]
        import_keyword = import_expr[2]
        imported = import_expr[3]
        return f'{mathml}<mtext>' \
               f'<mo class="keyword">{from_keyword} </mo>{module_name}' \
               f'<mo class="keyword"> {import_keyword} </mo>{imported}' \
               f'</mtext></mrow></math>'
    elif type(node) == ast.FunctionDef:
        function_definition = ast.unparse(node).split()[:2]
        def_keyword = f'<mo class="keyword">{function_definition[0]} </mo>'
        function_name = f'<mi class="def-function">{node.name}</mi>{function_definition[1].split(node.name)[-1]}'
        function_body = module_parser(ast.parse(ast.unparse(node.body)))
        return f'\n{mathml}<mrow><mtext>{def_keyword}{function_name}\n    {function_body}</mtext></mrow></math>\n'
    elif type(node) == ast.Return:
        return_expr = ast.unparse(node).split()
        return f'<mtext><mo class="keyword">{return_expr[0]} </mo>{return_expr[1]}</mtext>'
    elif type(node) == ast.Assign:
        targets = parse_targets(node.targets)
        expression = parse_expr(node.value)
        return f'{mathml}<mrow>{targets}<mo>{equal_sign}</mo>{expression}</mrow></math>'
    elif type(node) == ast.BinOp:
        return parse_bin_op(node)
    elif type(node) == ast.Name:
        name = astunparse.unparse(node)[:-1]
        name = math_names[name] if name in math_names else name
        return f'<mi>{name}</mi>'
    elif type(node) == ast.Constant:
        return f'<mn>{astunparse.unparse(node)[:-1]}</mn>'
    elif type(node) == ast.Call:
        return parse_call(node)
    elif type(node) == ast.For:
        return parse_for_loop(node)
    elif type(node) == ast.If:
        return parse_conditions(node)
    else:
        name_str = astunparse.unparse(node)[1:-1]
        return f'<mtext>{name_str}</mext>'


def parse_bin_op(node: ast.BinOp) -> str:
    right = parse_expr(node.right)
    left = parse_expr(node.left)
    if type(node.right) == ast.BinOp and priorities[type(node.op)] > priorities[type(node.right.op)]:
        right = f'{left_bracket}{right}{right_bracket}'
    if type(node.left) == ast.BinOp and priorities[type(node.op)] > priorities[type(node.left.op)]:
        left = f'{left_bracket}{left}{right_bracket}'
    if type(node.op) == ast.Mult:
        return f'{left}<mo>{pow_sign}</mo>{right}'
    elif type(node.op) == ast.Div:
        return f'<mfrac><mrow>{left}</mrow><mrow>{right}</mrow></mfrac>'
    elif type(node.op) == ast.Add:
        return f'{left}<mo>{plus_sign}</mo>{right}'
    elif type(node.op) == ast.Sub:
        return f'{left}<mo>{minus_sign}</mo>{right}'


def parse_call(node: ast.Call) -> str:
    if node.func.id == 'sqrt':
        return f'<msqrt><mrow>{parse_expr(node.args[0])}</mrow></msqrt>'
    else:
        return f'<mrow><mi>{node.func.id}</mi><mfenced>{parse_targets(node.args)}</mfenced></mrow>'


def parse_targets(targets_list: list) -> str:
    targets_str = []
    for target in targets_list:
        targets_str.append(' ' * target.col_offset + parse_expr(target))
    return '\n'.join(targets_str)


def parse_for_loop(node: ast.For) -> str:
    for_loop = f'{mathml}<mrow><mtext><mo style="color: #008000;">for </mo>' \
               f'<mi>{astunparse.unparse(node.target)[:-1]}</mi>' \
               f'<mo style="color: #008000;"> in </mo>{astunparse.unparse(node.iter)[:-1]}:' \
               f'</mtext><mrow></math>\n'
    for_loop += parse_targets(node.body)
    return for_loop


def parse_conditions(if_node: ast.If, nested=False) -> str:
    if_str = 'elif' if nested else 'if'
    if_condition = ' ' * if_node.col_offset + f'{mathml}<mrow><mtext><mo class="keyword">{if_str} </mo> {astunparse.unparse(if_node.test)[1:-2]}:</mext><mrow></math>\n'
    if_condition += parse_targets(if_node.body)
    for node in if_node.orelse:
        if type(node) == ast.If:
            if_condition += '\n' + parse_conditions(node, True)
        else:
            if_condition += '\n' + parse_else(if_node.orelse)
            break
    return if_condition


def parse_else(else_body: list) -> str:
    else_str = f'{mathml}<mrow><mtext><mo class="keyword">else:</mo></mtext></mrow></math>\n'
    else_str += parse_targets(else_body)
    return else_str


def module_parser(module):
    res = []
    for node in ast.iter_child_nodes(module):
        res.append(parse_expr(node))
    return '\n'.join(res)