import json
from abc import ABC
from ast import *
from astor import *
from pytexit import py2tex
import astunparse
from notebook.base.handlers import IPythonHandler

greek = {
    'tau': 'τ',
    'xi': 'ξ',
    'alpha': 'α',
    'Theta': 'Θ',
    'zeta': 'ζ',
    'Pi': 'Π',
    'Phi': 'φ',
    'Psi': 'Ψ',
    'Sigma': 'Σ',
    'chi': 'χ',
    'Delta': 'Δ',
    'theta': 'θ',
    'pi': 'π',
    'Omega': 'Φ',
    'nu': 'ν',
    'phi': 'ϕ',
    'psi': 'ψ',
    'Upsilon': 'Υ',
    'epsilon': 'ε',
    'omicron': 'ο',
    'beta': 'β',
    'rho': 'ρ',
    'delta': 'δ',
    'upsilon': 'υ',
    'omega': 'ω',
    'Gamma': 'Γ',
    'Lambda': 'Λ',
    'Xi': 'Ξ',
    'kappa': 'κ',
    'iota': 'ι',
    'mu': 'μ',
    'eta': 'η',
    'sigma': 'σ',
    'gamma': 'γ',
    'lambda': 'λ'
}


class PrettyPythonHandler(IPythonHandler, ABC):
    def post(self):
        python_code = self.get_json_body()['code']
        tree = parse(python_code)
        new_tree = fix_missing_locations(RewriteName().visit(tree))
        latex_code = to_source(new_tree)
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        latex_res = {'latex_code': latex_code}
        self.write(json.dumps(latex_res))


class RewriteName(NodeTransformer):
    def visit_Name(self, node):
        if node.id in greek:
            return Name(id=f'${greek[node.id]}$')
        return node

    def visit_BinOp(self, node: BinOp):
        try:
            return Name(
                id=f'{py2tex(astunparse.unparse(node), print_latex=False, print_formula=False, upperscript="#", lowerscript="#")}'
            )
        except:
            return node

    def visit_Attribute(self, node: Attribute):
        if node.attr in greek:
            return self.generic_visit(Attribute(attr=f'${greek[node.attr]}$', value=node.value))
        return self.generic_visit(node)
