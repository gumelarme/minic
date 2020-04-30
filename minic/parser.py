from typing import List, Tuple
from minic.scanner import FileScanner, Scanner, TokenType, Token
from minic.operation import Operation
from dataclasses import dataclass

class Parser:
    def __init__(self, scn: Scanner):
        self.scanner = scn
        self.types = ['int', 'void']

    def match(self, expected_token: Tuple[TokenType, str]):
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
            return self.declaration_list()
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

        res.insert(0, 'program')
        return res

    def type_declaration(self):
        res = [self.type_specifier()]
        if self.ct.ttype == TokenType.ID:
            res.append(self.match(self.ct))
        return res


    def var_declaration(self, res=None):
        res = self.type_declaration() if res == None else res

        res.insert(0, 'var')
        self.match(self._sep(';'))

        return res

    def func_declaration(self, res=None):
        res = self.type_declaration() if res == None else res

        self.match(self._sep('('))
        param = self.parameter_list()
        res.append(param)
        self.match(self._sep(')'))
        res .append(self.compound_stmt())
        res.insert(0, 'func')

        return res

    def parameter_list(self):
        # TODO stop searching if the first param is void
        res = [self.parameter()]
        if res[0] == 'void':
            res = ['params', res]
            return res

        while self.ct and ',' == self.ct.value:
            self.match(self._sep(','))
            res +=[self.parameter()]
        res = ['params', *res]
        return res

    def parameter(self):
        res = [self.type_specifier()]
        if res[0] == 'void':
            return res[0]
        if self.ct.ttype == TokenType.ID:
            # res.append(self.match((TokenType.ID, '')))
            res.append(self.match(Token(TokenType.ID, '')))

        return res

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
            res.append(self.iteration_statement())
        elif self.ct.value in ['switch', 'if']:
            res.append(self.selection_stmt())
        elif self.ct.value == '{':
            res.append(self.compound_stmt())
        elif  self.ct.value in ['default', 'case']:
            res.append(self.labeled_stmt())
        else:
            if self.ct.ttype == TokenType.ID:
                var = self.match(self.ct)
                if self.ct.value == ':':
                    res += [self.labeled_stmt(var)]
                else:
                    res += [*self.exp_stmt(var)]

        return self.first(res)

    def compound_stmt(self):
        res = []

        # self.match((TokenType.SEPARATOR, '{'))
        self.match(self._sep('{'))
        while self.ct.value != '}':
            res.append(self.statement())

        # self.match((TokenType.SEPARATOR, '}'))
        self.match(self._sep('}'))

        res.insert(0, 'body')
        return res

    def iteration_statement(self):
        res = []
        if self.ct.value == 'for':
            res += [self.match(Token(TokenType.KEYWORD, 'for'))]
            self.match(self._sep('('))

            for x in range(3):
                if x == 2 and self.ct.value == ')':
                    res.append(None)
                else:
                    res += [self.optional_exp()]
                    if x != 2:
                        self.match(self._sep(';'))

            self.match(self._sep(')'))
            res += [self.statement()]
        elif self.ct.value == 'while':
            res += [self.match(Token(TokenType.KEYWORD, 'while'))]
            self.match(self._sep('('))
            res += [self.exp()]
            self.match(self._sep(')'))
            res += [self.statement()]

        return res

    def selection_stmt(self):
        res = []
        if self.ct.value == 'if':
            res += [self.match(Token(TokenType.KEYWORD, 'if'))]
            self.match(self._sep('('))
            res += [self.exp()]
            self.match(self._sep(')'))

            #if body
            stmt = self.statement()
            if stmt[0] != 'body':
                res.append(['body', stmt])
            else:
                res += [stmt]

            if self.ct and self.ct.value == 'else':
                self.match(Token(TokenType.KEYWORD, 'else'))

                else_stmt = self.statement()
                if else_stmt[0] == 'body':
                    else_stmt[0] = 'else'
                else:
                    else_stmt = ['else', else_stmt]
                res.append(else_stmt)

        # TODO switch still behave like if, fix it
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
        if value == 'return':
            res = [self.match(Token(TokenType.KEYWORD, 'return'))]

            opx = self.optional_exp()
            # if return nothing
            # "not opx" expression evaluate '0' as false
            if not opx and opx != 0: 
                return res

            res += [opx if type(opx) == list else opx]
        elif value == 'goto':
            res = [self.match(self.ct)]
            res += [self.match(Token(TokenType.ID, ''))]
        elif value == 'break':
            res = [self.match(self.ct)]

        self.match(self._sep(';'))
        return res

    def exp_stmt(self, var=None):
        res = self.optional_exp(var)
        self.match(self._sep(';'))
        return res

    def labeled_stmt(self, var=None):
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
        if self.ct.value != ';':
            x = self.exp(var)
            return x
        self.match(self._sep(';'))
        return []

    def exp(self, var=None):
        res = []
        if var != None or self.ct.ttype == TokenType.ID:
            if var == None:
                var = self.variable()

            if self.ct.ttype == TokenType.ASSIGNMENT:
                assign = self.assignment_exp(var)
                res.append(assign)
            else:
                res.append(self.conditional_exp(var))
        else:
            res.append(self.conditional_exp(None))

        return self.first(res)

    def assignment_exp(self, var=None):
        var = self.variable() if var == None else var

        res = [self.match(Token(TokenType.ASSIGNMENT, '='))]
        res.append(var)
        res.append(self.exp())
        return res

    def variable(self):
        res = ''
        if self.ct.ttype == TokenType.ID:
            res += self.match(Token(TokenType.ID, ''))

        if self.ct == self._sep('['):
            res += self.match(self._sep('['))
            res += str(self.match(Token(TokenType.CONSTANT, '')))
            res += self.match(self._sep(']'))

        elif self.ct == self._sep('.'):
            res += self.match(self._sep('.'))
            res += self.match(self.ct)

        return res

    def call_function(self, name=None):
        res = ['call-func']
        if name:
            res += [name]
        elif self.ct.ttype == TokenType.ID:
            res += [self.match(self.ct)]

        self.match(self._sep('('))
        res.append(self.argument_list())
        self.match(self._sep(')'))
        return res

    def argument_list(self):
        res = ['args']
        if self.ct.value == ')':
            return res

        res += [self.exp()]
        while self.ct and self.ct.value == ',':
            self.match(self.ct)
            res.append(self.exp())
        return self.first(res)

    def conditional_exp(self, var=None):
        res = [self.add_exp(var)]
        rel_operator = ['<', '>', '>=', '<=', '==', '!=']
        while self.ct and self.ct.value in rel_operator:
            if len(res) > 1:
                res = [res]

            res.insert(0, self.match(self.ct))
            res += [self.add_exp()]

        return self.first(res)

    def add_exp(self, var=None):
        res = [self.multi_exp(var)]
        while self.ct and self.ct.value in ['+', '-']:
            if len(res) > 1:
                res = [res]

            res.insert(0, self.match(self.ct))
            res += [self.multi_exp()]

        return self.first(res)

    def multi_exp(self, var=None):
        res = [self.pri_exp(var)]
        while self.ct and self.ct.value in ['*', '/']:
            if len(res) > 1:
                res = [res]

            res.insert(0, self.match(self.ct))
            res += [self.pri_exp()]

        return self.first(res)

    def pri_exp(self, var=None):
        token = self.ct.ttype
        value = self.ct.value

        if var:
            if value == '(':
                return self.call_function(var)
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
            self.match(self._sep(')'))
            return res
        elif token == TokenType.CONSTANT:
            return self.match(Token(TokenType.CONSTANT, ''))
        else:
            # print(self.ct, var)
            raise Exception(f'Unexpected {self.ct}')
