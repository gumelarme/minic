from typing import List

import minic.node as nd
import minic.symboltable as symb
from minic.exceptions import SemanticError


# TODO: For, While, Switch
class NodeVisitor:
    current_scope: symb.ScopedSymbolTable
    def __init__(self, root: nd.Node):
        self.root = root

    def start(self):
        self.visit(self.root)

    def visit(self, node: nd.Node):
        method_name = "visit_" + node.__class__.__name__
        method = getattr(self, method_name)
        method(node)

    def visit_block(self, nodes: List[nd.Node]):
        for x in nodes:
            self.visit(x)

    def visit_Program(self, node: nd.Program):
        scope_name = '<global>'
        print(f"ENTER scope: {scope_name}")

        scope = symb.ScopedSymbolTable(scope_name, 1, verbose=True)
        scope.init_builtin()
        self.current_scope = scope

        self.visit_block(node.declarations)
        print(scope)

        print(f"LEAVING Scope: {scope_name}")

    def visit_VarDecl(self, node: nd.VarDecl):
        if self.current_scope.lookup(node.name, deep=False):
            raise Exception(f"Symbol {node.name} is already declared")

        int_type = self.current_scope.lookup(node.type)
        symbol = nd.VarSymbol(node.name, int_type)
        self.current_scope.insert(symbol)

    def visit_BinOp(self, node: nd.BinOp):
        # print("Binary operation: ", node.operator);
        self.visit(node.left)
        self.visit(node.right)

    def visit_AssignmentOp(self, node: nd.AssignmentOp):
        self.visit(node.target)
        self.visit(node.value)

    def visit_RelOp(self, node: nd.RelOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_JumpStmt(self, node: nd.JumpStmt):
        # TODO do something with keyword?
        self.visit(node.value)

    def visit_IfOp(self, node: nd.IfOp):
        # TODO shoudl else block be directly accessed
        self.visit(node.condition)
        self.visit_block(node.body)
        # self.visit_block(node.else_body)

    def visit_ForHeader(self, node: nd.ForHeader):
        self.visit(node.first)
        self.visit(node.second)
        self.visit(node.third)

    def visit_ForLoop(self, node: nd.ForLoop):
        self.visit(node.header)
        self.visit_block(node.body)
        # self.visit_block(node.else_body)

    def visit_WhileLoop(self, node: nd.WhileLoop):
        self.visit(node.condition)
        self.visit_block(node.body)


    def visit_CallFuncOp(self, node: nd.CallFuncOp):
        func = self.current_scope.lookup(node.name)
        name = node.name
        if type(func) != symb.FunctionSymbol:
            raise SemanticError(
                node,
                self.current_scope,
                f"'{name}' is not a function"
            )

        # from here is guaranteed to be FuncDecl
        func: nd.FuncDecl
        if len(func.params) != len(node.args):
            raise SemanticError(
                node,
                self.current_scope,
                f"Parameter count at '{name}' method did not match"
            )

        # for i, param in enumerate(func.params):
            # TODO check type before visit another node
            # if param.type == node.args:
            #     pass
           
        for i, arg in enumerate(node.args):
            self.visit(arg)


    def visit_Var(self, node: nd.Var):
        name = node.value
        v = self.current_scope.lookup(name)
        if not v:
            raise SemanticError(
                node,
                self.current_scope,
                f"Variable '{name}' has not been declared"
            )

    def visit_Num(self, node: nd.Num):
        print("Constant: ", node.value)


    def visit_FuncDecl(self, node: nd.FuncDecl):
        name  = node.name
        rettype = self.current_scope.lookup(node.ret_type)
        func = symb.FunctionSymbol(name, rettype)
        self.current_scope.insert(func)
        print("ENTER scope:", name)

        scope = symb.ScopedSymbolTable(
            name,
            self.current_scope.level + 1,
            self.current_scope,
            verbose=True
        )

        self.current_scope = scope

        # registering parameter
        params = []
        if node.params[0].type != 'void':
            for x in node.params:
                var = nd.VarSymbol(x.name, self.current_scope.lookup(x.type))
                self.visit_VarDecl(x)
                # self.current_scope.insert(var)
                params += [var]

        func.params = params

        self.visit_block(node.body)

        self.current_scope = self.current_scope.parent_scope
        print(scope)
        print("LEAVING scope:", name)
