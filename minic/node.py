from typing import List, Union, Tuple

from dataclasses import dataclass, field
# from pydantic.dataclasses import dataclass, field


from pydantic import StrictInt
from minic.symboltable import SymbolTable, VarSymbol, FunctionSymbol, TypeSymbol

@dataclass
class Node:
    linum: StrictInt
    # op: List

    # def __init__(self, linum, op):
    #     self.linum = linum
    #     self.op = op

    def _stmt_to_list(self, stmt):
        if stmt == None:
            return []

        return stmt if type(stmt) == list else [stmt]

    def get_tree(self):
        result = []
        for x in self.op:
            if type(x) == Node:
                result += [x.get_tree()]
            elif type(x) == list:
                result.append([v.get_tree() if type(v) == Node else v for v in x])
            else:
                result += [x]

        return result

    def get_tree_str(self):
        return str(self.get_tree()).replace("'", "").replace(",", "")

@dataclass
class Num(Node):
    value: StrictInt

    def __repr__(self):
        return f"Num({self.value})"

@dataclass
class Var(Node):
    value: str
    # it can be an index or an object properties
    prop: Union[StrictInt, str] = None
    type: str = 'variable'

    def __init__(self, linum, value, prop=None):
        self.linum = linum
        self.value = value
        self.prop = prop

        dic = {int:'array', str:'object'}
        self.type = dic.get(type(self.prop), 'variable')

    def __repr__(self):
        inside = f"{self.value}"

        if self.type == 'array':
            inside = f"{self.value}[{prop}]"
        elif self.type == 'object':
            inside = f"{self.value}.{prop}"

        return f"Var({inside})"

@dataclass
class BinOp(Node):
    operator: str
    left: Union['BinOp', Num]
    right: Union['BinOp', Num]

    def __repr__(self):
        return "BinOp[{linum}]({op}, {l}, {r})".format(
            linum= self.linum,
            op=self.operator,
            l=self.left,
            r=self.right
        )

@dataclass
class RelOp(Node):
    operator: str
    left: Union['RelOp', BinOp, Num]
    right: Union['RelOp', BinOp, Num]

    def __repr__(self):
        return "RelOp[{linum}]({op}, {l}, {r})".format(
            linum= self.linum,
            op=self.operator,
            l=self.left,
            r=self.right
        )

@dataclass
class IfOp(Node):
    condition: RelOp
    body: List
    else_body: List = None

    def __init__(self, linum, condition, body, else_body=None):
        self.linum = linum
        self.condition = condition
        self.body = self._stmt_to_list(body)
        self.else_body = self._stmt_to_list(else_body)
        pass


@dataclass
class ForHeader:
    first: Node = None
    second: Node = None
    third: Node = None

@dataclass
class ForLoop(Node):
    header: ForHeader
    body: List

    def __init__(self, linum, header, body=None):
        self.linum = linum
        self.header = header
        self.body = self._stmt_to_list(body)

@dataclass
class WhileLoop(Node):
    condition: Node
    body: List

    def __init__(self, linum, cond, body=None):
        self.linum = linum
        self.condition = cond
        self.body = self._stmt_to_list(body)


@dataclass
class CallFuncOp(Node):
    name: str
    args: List[Union[Num, Var, BinOp, RelOp, 'CallFuncOp']] = None

@dataclass
class AssignmentOp(Node):
    target: str
    value: Union[RelOp, BinOp, CallFuncOp, Num]

@dataclass
class LabeledStmt(Node):
    label: str
    value: Union[list, BinOp, RelOp, CallFuncOp, AssignmentOp, Var, Num, str] = None

@dataclass
class JumpStmt(Node):
    keyword: str
    value: Union[BinOp, RelOp, CallFuncOp, AssignmentOp, Var, Num, str] = None

@dataclass
class ParamDecl(Node):
    type: str
    name: str

@dataclass
class FuncDecl(Node):
    ret_type: str
    name: str
    params: List[ParamDecl] = None
    body: List = None

@dataclass
class VarDecl(Node):
    type: str
    name: str

@dataclass
class Program(Node):
    declarations: List[Union[ParamDecl, VarDecl]]

# TODO: For, While, Switch

class NodeVisitor:
    def __init__(self, root: Node):
        self.root = root
        self.symtab = SymbolTable()

    def start(self):
        self.visit(self.root)
        print(self.symtab)

    def visit(self, node: Node):
        method_name = "visit_" + node.name
        method = getattr(self, method_name)
        method(node)

    def visit_block(self, nodes: List[Node]):
        for x in nodes:
            self.visit(x)

    def visit_program(self, node: Node):
        self.visit_block(node.op[1:])

    def visit_var(self, node: Var):
        int_type = self.symtab.lookup(node.op[1])
        symbol = VarSymbol(node.op[2], int_type)
        self.symtab.insert(symbol)

    def visit_func(self, node: Node):
        data = node.op[1:]
        rettype = self.symtab.lookup(data[0])
        func = FunctionSymbol(data[1], rettype, data[2][1])
        self.symtab.insert(func)
