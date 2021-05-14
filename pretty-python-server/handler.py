import ast
import json
from abc import ABC

import astunparse
import pytexit
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
    if type(node) == ast.Assign:
        return pytexit.py2tex(
            astunparse.unparse(node),
            print_formula=False,
            print_latex=False,
            simplify_multipliers=False
        )


def main_parse(module):
    res = []
    for node in ast.iter_child_nodes(module):
        res.append(parse_expr(node))
    for i in range(len(res)):
        res[i] = res[i][1:-1]
        res[i] = res[i].replace('times', 'cdot ')
    return '\n\n'.join(res)
