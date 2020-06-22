from typing import List, Tuple, Union

from minic.scanner import FileScanner, Scanner, TokenType, Token
import minic.node as nd
from pydantic.dataclasses import dataclass

class Parser:
    def __init__(self, scn: Scanner):
        self.scanner = scn
        self.types = ['int', 'void']
    def __repr__(self):
        t = f"<Parser> :: {type(self.scanner)} {{ \n"
        t += f"\t current_token: {self.ct}\n"
        t += f"\t current_token: {self.ct}\n"
        t += "}"
        return t


    def match(self, expected_token: Tuple[TokenType, str]):
        if not self.ct:
            raise Exception("Current token value is None")

        err_msg = f"Expecting {expected_token}, instead of {self.ct}"
        if self.ct.ttype != expected_token.ttype:
            raise Exception(err_msg)

        if expected_token.ttype == TokenType.SEPARATOR:
            if self.ct.value != expected_token.value:
                raise Exception(err_msg)

        temp, self.ct = self.ct, self.scanner.next_token()
        if temp.ttype == TokenType.CONSTANT:
            return int(temp.value.strip())
        return temp.value


    def _sep(self, val: str):
        return Token(TokenType.SEPARATOR, val, -1)

    def first(self, arr):
        return arr[0] if len(arr) == 1 else arr

    # program
    def start(self, startfrom=None):
        self.ct: Token = self.scanner.next_token()
        if startfrom == None:
            return nd.Program(1, self.declaration_list()) 
        else:
            return getattr(self, startfrom)()

    def declaration_list(self):
        res = []
        while self.scanner.is_next():
            # spread
            typedec = [*self.type_declaration()]
            if self.ct.value == ';':
                res += [self.var_declaration(typedec)]
            else:
                res += [self.func_declaration(typedec)]

        return res

    def type_declaration(self):
        res = [self.type_specifier()]
        if self.ct.ttype == TokenType.ID:
            res.append(self.match(self.ct))
        return res


    def var_declaration(self, res=None):
        res = self.type_declaration() if res == None else res
        self.match(self._sep(';'))

        return nd.VarDecl(1, *res)

    def func_declaration(self, res=None):
        linum = self.ct.linum
        res = self.type_declaration() if res == None else res
        rettype, name = res

        self.match(self._sep('('))
        params = self.parameter_list()
        self.match(self._sep(')'))

        body = self.compound_stmt()

        return nd.FuncDecl(linum, rettype, name, params, body)

    def parameter_list(self):
        # TODO raise error if there is another param after void
        res = [self.parameter()]
        if res[0].type == 'void':
            return res

        while self.ct and ',' == self.ct.value:
            self.match(self._sep(','))
            res +=[self.parameter()]
        return res

    def parameter(self):
        linum = self.ct.linum
        t, name = self.type_specifier(), None

        if self.ct and t != 'void' and self.ct.ttype == TokenType.ID:
            name = self.match(Token(TokenType.ID, ''))

        # elif self.ct and t == 'void' and self.ct.ttype == TokenType.ID:
        #     raise Exception('void parameter cannot followed by ID')


        return nd.ParamDecl(linum, t, name)
    def type_specifier(self):
        # token, word = self.ct
        if self.ct.ttype != TokenType.KEYWORD:
            raise Exception(f'Err: \'{word}\' expected a keyword')

        if self.ct.value in self.types:
            return self.match(self.ct)
        else:
            raise Exception(f'Err: \'{word}\' is not a type')

    def statement(self):
        # TODO
        # * local-declaration
        # * compound -> recurse
        # * expression -> * assignment, * arithmetic, * boolean
        # selection -> +if select
        # labeled -> goto, default
        # iteration -> +while +for
        # *jump -> *return, *break, *goto

        res = []
        if self.ct.value in ['return', 'goto', 'break']:
            res += [self.jump_stmt()]
        elif self.ct.value in self.types:
            res.append(self.var_declaration())
        elif self.ct.value in ['for', 'while']:
            res.append(self.iteration_stmt())
        elif self.ct.value in ['switch', 'if']:
            res.append(self.selection_stmt())
        elif self.ct.value == '{':
            res.append(self.compound_stmt())
        elif  self.ct.value in ['default', 'case']:
            res.append(self.labeled_stmt())
        else:
            if self.ct.ttype == TokenType.ID:
                var = self.variable()
                if self.ct.value == ':':
                    res += [self.labeled_stmt(var)]
                else:
                    res += [self.exp_stmt(var)]
            else:
                raise Exception('Unexpected {}'.format(self.ct))

        return self.first(res)

    def compound_stmt(self):
        res = []

        # self.match((tokentype.separator, '{'))
        self.match(self._sep('{'))
        while self.ct.value != '}':
            res.append(self.statement())

        # self.match((tokentype.separator, '}'))
        self.match(self._sep('}'))
        return res

    def iteration_stmt(self):
        linum = self.ct.linum
        if self.ct.value == 'for':
            self.match(Token(TokenType.KEYWORD, 'for'))
            self.match(self._sep('('))

            header = [None] * 3
            for i in range(3):
                if i < 2:
                    header[i] = self.optional_exp()
                    self.match(self._sep(';'))

                elif self.ct != self._sep(')'):
                    header[i] = self.optional_exp()

            self.match(self._sep(')'))
            body = self.statement()

            return nd.ForLoop(linum, nd.ForHeader(*header), body)

        elif self.ct.value == 'while':
            self.match(Token(TokenType.KEYWORD, 'while'))
            self.match(self._sep('('))
            cond = self.exp()
            self.match(self._sep(')'))
            body = self.statement()

            return nd.WhileLoop(linum, cond, body)

    def selection_stmt(self):
        """
        TODO switch still behave like if, fix it
        TODO make a test for switch
        """
        res = []
        if self.ct.value == 'if':
            key = self.match(Token(TokenType.KEYWORD, 'if'))
            self.match(self._sep('('))
            condition = self.exp()
            self.match(self._sep(')'))

            #if body
            stmt, else_stmt = self.statement(), []
            # if stmt[0] != 'body':
            #     res.append(['body', stmt])
            # else:
            #     res += [stmt]

            if self.ct and self.ct.value == 'else':
                self.match(Token(TokenType.KEYWORD, 'else'))

                else_stmt = self.statement()
                # if else_stmt[0] == 'body':
                #     else_stmt[0] = 'else'
                # else:
                #     else_stmt = ['else', else_stmt]
                res.append(else_stmt)

            return nd.IfOp(1, condition, stmt, else_stmt)
        elif self.ct.value == 'switch':
            res += [self.match(Token(TokenType.KEYWORD, 'switch'))]
            self.match(self._sep('('))
            res += [self.exp()]
            self.match(self._sep(')'))
            res += [self.statement()]

        return res

    def jump_stmt(self):
        res = []
        token = self.ct.ttype
        value = self.ct.value
        linum = self.ct.linum

        key, stmt = [None] * 2

        if value == 'return':
            key = self.match(Token(TokenType.KEYWORD, 'return'))

            stmt = self.optional_exp()
            self.match(self._sep(';'))
            # if return nothing
            # "not opx" expression evaluate '0' as false
            # if not opx and opx != 0: 
            #     return res
            # res += [opx if type(opx) == list else opx]
            return nd.JumpStmt(linum, key, stmt)
        elif value == 'goto':
            key = self.match(self.ct)
            stmt = self.match(Token(TokenType.ID, ''))
        elif value == 'break':
            key = self.match(self.ct)

        self.match(self._sep(';'))

        return nd.JumpStmt(linum, key, stmt)

    def exp_stmt(self, var=None):
        '''
        TODO: Make test
        '''
        res = self.optional_exp(var)
        self.match(self._sep(';'))
        return res

    def labeled_stmt(self, var=None):
        '''
        TODO: Make test
        '''
        res = []
        if self.ct.value == 'default':
            res += [self.match(self.ct)]
        elif var != None:
            res += ['label', var]
        elif self.ct.value == 'case':
            res += [self.match(self.ct)]
            res += [self.conditional_exp()]

        self.match(self._sep(':'))
        res += [self.statement()]
        return res

    def optional_exp(self, var=None):
        '''
        TODO: Make test
        '''
        if self.ct.value != ';':
            x = self.exp(var)
            return x

        # self.match(self._sep(';'))
        return None

    def exp(self, var=None):
        '''
        TODO: Make test
        '''
        exp = None

        if var != None or self.ct.ttype == TokenType.ID:
            if var == None:
                var = self.variable()

            if self.ct:
                if self.ct.ttype == TokenType.ASSIGNMENT:
                    exp = self.assignment_exp(var)
                else:
                    exp =  self.conditional_exp(var)
            else:
                exp = var
        else:
            exp = self.conditional_exp(None)

        return exp 

    def assignment_exp(self, var=None):
        var = self.variable() if var == None else var

        self.match(Token(TokenType.ASSIGNMENT, '='))
        exp = self.exp()
        return nd.AssignmentOp(1, var, exp)

    def variable(self):
        linum = self.ct.linum
        name, prop = '', None

        if self.ct.ttype == TokenType.ID:
            name = self.match(Token(TokenType.ID, ''))
        else:
            raise Exception(f'Token type is not ID: {self.ct}')

        if self.ct == self._sep('['):
            self.match(self._sep('['))
            prop = self.match(Token(TokenType.CONSTANT, ''))
            self.match(self._sep(']'))

        elif self.ct == self._sep('.'):
            self.match(self._sep('.'))
            prop = self.match(self.ct)

        if prop:
            return nd.Var(linum, name, prop)

        return nd.Var(linum, name)

    def call_function(self, name=None):
        linum = self.ct.linum

        if name == None and  self.ct.ttype == TokenType.ID:
            name = self.match(self.ct)

        self.match(self._sep('('))

        args = self.argument_list()

        self.match(self._sep(')'))

        return nd.CallFuncOp(linum, name, args)

    def argument_list(self):
        if self.ct.value == ')':
            return None

        res = [self.exp()]
        while self.ct and self.ct.value == ',':
            self.match(self.ct)
            res.append(self.exp())

        return res

    def conditional_exp(self, var=None):
        linum = self.ct.linum
        left = self.add_exp(var)
        while self.ct and self.ct.value in ['<', '>', '>=', '<=', '==', '!=']:
            op = self.match(self.ct)
            right = self.add_exp()
            left = nd.RelOp(linum, op, left, right)

        return left

    def add_exp(self, var=None):
        linum = self.ct.linum
        left = self.multi_exp(var)
        while self.ct and self.ct.value in ['+', '-']:
            op = self.match(self.ct)
            right = self.multi_exp()
            left = nd.BinOp(linum, op, left, right)

        return left

    def multi_exp(self, var=None):
        linum = self.ct.linum
        left = self.pri_exp(var)
        while self.ct and self.ct.value in ['*', '/']:
            op = self.match(self.ct)
            right = self.pri_exp()
            left = nd.BinOp(linum, op, left, right)

        return left

    def pri_exp(self, var: nd.Var =None) -> Union[nd.Num, nd.Var, nd.CallFuncOp, nd.BinOp, nd.RelOp]:
        linum = self.ct.linum
        token = self.ct.ttype
        value = self.ct.value

        if var:
            if value == '(':
                return self.call_function(var.value)
            else:
                return var

        if token == TokenType.ID:
            var = self.variable()
            if self.ct and self.ct.value == '(':
                return self.pri_exp(var)
            else:
                return var

        elif value == '(':
            self.match(self._sep('('))
            res = self.add_exp()
            self.match(self._sep(')'))  # 
            return res
        elif token == TokenType.CONSTANT:
            num = self.match(Token(TokenType.CONSTANT, ''))
            return nd.Num(linum, num)
            # return self.match(Token(TokenType.CONSTANT, ''))
        else:
            # print(self.ct, var)
            raise Exception(f'Unexpected {self.ct}')
