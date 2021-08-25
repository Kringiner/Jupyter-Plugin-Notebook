import json
from abc import ABC
from ast import *
from astor import *
import re
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

allow_module = ['np', 'math']


class PrettyPythonHandler(IPythonHandler, ABC):
    def post(self):
        python_code = self.get_json_body()['code']
        tree = parse(python_code)
        new_tree = fix_missing_locations(LatexTransformer().visit(tree))
        latex_code = to_source(new_tree)
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        latex_res = {'latex_code': latex_code}
        self.write(json.dumps(latex_res))


class LatexVisitor(NodeVisitor):

    def __init__(self):
        super(LatexVisitor, self).__init__()
        self.precdic = {
            "Pow": 700,
            "Div": 400,
            "FloorDiv": 400,
            "Mult": 400,
            "Invert": 800,
            "Compare": 300,
            "Uadd": 800,
            "Not": 800,
            "USub": 800,
            "Num": 1000,
            "Constant": 1000,
            "Assign": 300,
            "Sub": 300,
            "Add": 300,
            "Mod": 500,
            "ListComp": 1000,
            "list": 1000,
            "Call": 1000,
            "Name": 1000,
            "Subscript": 1000,
            "Attribute": 1000,
            "BinOp": 300,
        }

    @staticmethod
    def brackets(expression):
        return r"{{{0}}}".format(expression)

    @staticmethod
    def parenthesis(expression):
        return r"\left({0}\right)".format(expression)

    @staticmethod
    def operator(func, args=None):
        if args is None:
            return r"\operatorname{{{0}}}".format(func)
        else:
            return r"\operatorname{{{0}}}\left({1}\right)".format(func, args)

    def prec(self, n):
        if n.__class__.__name__ in self.precdic:
            return self.precdic[n.__class__.__name__]
        else:
            return 0

    def visit_list(self, n):
        self.generic_visit(n)

    def division_self(self, up, down):
        return r"\frac{0}{1}".format(self.brackets(up), self.brackets(down))

    def group(self, expression):
        if len(expression) == 1:
            return expression
        else:
            return self.brackets(expression)

    def sqrt(self, args):
        return r"\sqrt{0}".format(self.brackets(args))

    def power(self, expression, power_n):
        return r"{0}^{1}".format(self.group(expression), self.group(power_n))

    def parse_args(self, func):
        args = [*map(self.visit, func.args)] + [*map(self.visit, func.keywords)]
        return ', '.join(args)

    def visit_Attribute(self, node):
        attrs = []
        while not isinstance(node, Name):
            attrs.append(node.attr)
            node = node.value
        module = node.id.replace("_", "\\_")
        str_attr = '.'.join(attrs).replace("_", "\\_")
        parsed_attr = f'{module}.{str_attr}'
        if re.match(rf'^({"|".join(allow_module)})[.]pi$', parsed_attr):
            return greek['pi']
        return parsed_attr

    def visit_Call(self, n):
        func = self.visit(n.func)

        args = self.parse_args(n)

        if re.match(rf'^({"|".join(allow_module)})[.]sqrt$', func):
            return self.sqrt(args)
        elif re.match(rf'^({"|".join(allow_module)})[.]gamma$', func):
            return self.operator(greek['Gamma'], args)
        elif re.match(rf'^({"|".join(allow_module)})[.]exp$', func):
            return self.power('e', args)
        else:
            return self.operator(func, args)

    def visit_UnaryOp(self, n):
        if self.prec(n.op) > self.prec(n.operand):
            return r"{0}{1}".format(self.visit(n.op), self.parenthesis(self.visit(n.operand)))
        else:
            return r"{0}{1}".format(self.visit(n.op), self.visit(n.operand))

    def prec_unary_op(self, n):
        return self.prec(n.op)

    def visit_Subscript(self, node):
        return f'{self.visit(node.value)}[{self.visit(node.slice)}]'

    def visit_BinOp(self, n):

        if self.prec(n.op) > self.prec(n.left):
            left = self.parenthesis(self.visit(n.left))
        elif isinstance(n.op, Pow) and self.prec(n.op) == self.prec(n.left):
            left = self.parenthesis(self.visit(n.left))
        else:
            left = self.visit(n.left)
        if self.prec(n.op) > self.prec(n.right):
            right = self.parenthesis(self.visit(n.right))
        else:
            right = self.visit(n.right)

        if isinstance(n.op, Div):
            return self.division_self(self.visit(n.left), self.visit(n.right))
        elif isinstance(n.op, FloorDiv):
            return r"\left\lfloor\frac{%s}{%s}\right\rfloor" % (
                self.visit(n.left),
                self.visit(n.right),
            )
        elif isinstance(n.op, Pow):
            return self.power(left, self.visit(n.right))
        elif isinstance(n.op, Mult):
            return r"{0}{1}{2}".format(left, self.visit(n.op), right)
        else:
            return r"{0}{1}{2}".format(left, self.visit(n.op), right)

    def prec_bin_op(self, n):
        return self.prec(n.op)

    def visit_Sub(self, n):
        return "-"

    def visit_Add(self, n):
        return "+"

    def visit_Mult(self, n):
        return " \\cdot "

    def visit_Mod(self, n):
        return " \\bmod "

    def visit_LShift(self, n):
        return self.operator("shiftLeft")

    def visit_RShift(self, n):
        return self.operator("shiftRight")

    def visit_BitOr(self, n):
        return self.operator("or")

    def visit_BitXor(self, n):
        return self.operator("xor")

    def visit_BitAnd(self, n):
        return self.operator("and")

    def visit_Invert(self, n):
        return self.operator("invert")

    def visit_Not(self, n):
        return "\\neg"

    def visit_UAdd(self, n):
        return "+"

    def visit_Constant(self, node):
        return '\"' + node.value + '\"' if isinstance(node.value, str) else str(node.value)

    def visit_USub(self, n):
        return "-"

    def visit_Name(self, node):
        if node.id in greek:
            return greek[node.id]
        return node.id.replace('_', '\\_')

    def visit_keyword(self, node):
        return f'{node.arg}={self.visit(node.value)}'

    def visit_Slice(self, node):
        return f'{to_source(node)[:-1:]}'

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Num(self, n):
        return str(n.n)

    def visit_Assign(self, n):
        return r"%s=%s" % (self.visit(n.targets[0]), self.visit(n.value))

    def visit_Compare(self, n):
        def visit_op(op):
            if isinstance(op, Lt):
                return "<"
            elif isinstance(op, LtE):
                return "<="
            elif isinstance(op, Gt):
                return ">"
            elif isinstance(op, GtE):
                return ">="
            elif isinstance(op, Eq):
                return "="
            else:
                raise ValueError("Unknown comparator", op.__class__)

        return r"%s%s" % (
            self.visit(n.left),
            "".join(
                [
                    "%s%s" % (visit_op(n.ops[i]), self.visit(n.comparators[i]))
                    for i in range(len(n.comparators))
                ]
            ),
        )


class LatexTransformer(NodeTransformer):
    @staticmethod
    def make_name_latex_node(node):
        return Name(id=f'$${LatexVisitor().visit(node)}$$')

    @staticmethod
    def make_name_node(node):
        return Name(id=f'{LatexVisitor().visit(node)}')

    def try_parse(self, node):
        try:
            return self.make_name_latex_node(node)
        except:
            return node

    def visit_Name(self, node):
        return self.make_name_node(node)

    def visit_BinOp(self, node: BinOp):
        return self.try_parse(node)

    def visit_Attribute(self, node: Attribute):
        return self.make_name_node(node)

    def visit_Call(self, node: Call):
        return self.try_parse(node)
