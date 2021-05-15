import ast
import json
from abc import ABC

import astunparse
import pytexit
import latex2mathml.converter as math_ml_converter
from notebook.base.handlers import IPythonHandler


class PrettyPythonHandler(IPythonHandler, ABC):
    def post(self):
        python_code = self.get_json_body()['code']
        latex_code = main_parse(ast.parse(python_code))
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        latex_res = {'latex_code': latex_code}
        self.write(json.dumps(latex_res))


def parse_expr(node):
    if type(node) == ast.Assign and type(node.value) == ast.BinOp:
        latex_str = pytexit.py2tex(astunparse.unparse(node), print_formula=False, print_latex=False)[2:-2]
        return math_ml_converter.convert(latex_str)
    elif type(node) == ast.For:
        for_main_str = f'<pre>\tfor {astunparse.unparse(node.target)[:-1]} in {astunparse.unparse(node.iter)[:-1]}:</pre>'
        for_body = f'<div>{loops_body_parser(node.body)}</div>'
        return for_main_str + for_body
    else:
        return f'<pre>{astunparse.unparse(node)[1:-1]}</pre>'


def main_parse(module):
    res = []
    for node in ast.iter_child_nodes(module):
        res.append(parse_expr(node))
    return '\n'.join(res)


def loops_body_parser(loop_body):
    res = []
    for node in loop_body:
        res.append(parse_expr(node))
    return '\n'.join(res)
