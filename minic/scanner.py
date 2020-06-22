from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from copy import deepcopy


class TokenType(Enum):
    START = 0
    ID = 1
    CONSTANT = 2
    KEYWORD = 3
    ARITHMETIC_OPERATOR = 4
    REL_OPERATOR = 5
    SEPARATOR = 6
    ASSIGNMENT = 7

@dataclass(init=True, eq=True)
class Token:
    ttype: TokenType
    value: str
    linum: int = -1

    def __eq__(self, other: Token):
        """Skipping linum for equality"""
        if other == None:
            return False

        if self.ttype != other.ttype:
            return False

        if self.value != other.value:
            return False

        return True


class Scanner:
    def __init__(self):
        self.init_keywords()

    def init_keywords(self):
        keys = 'else if switch case default int void struct return break goto while for'
        self.keyword = [x for x in keys.split(" ")]
        self.arithmetic_operator= '+-*/'
        self.rel_operator= [x for x in '< <= > >= == !='.split(" ")]
        self.rel_start= [x for x in '< > = !'.split(" ")]
        self.separator = '(){};:,[].'

    def open(self) -> Scanner:
        return self.__enter__()

    def close(self):
        self.__exit__(None, None, None)

    def spit(self) -> str:
        pass

    def __enter__(self) -> ScannerObject:
        pass

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def is_next(self) -> bool:
        pass

    def back(self):
        pass

    def next_char(self) -> str:
        pass

    def get_linum(self) -> int:
        return -1

    def next_token(self) -> (TokenType, str):
        # cur_state = TokenType.START
        c = self.next_char() # Get char
        token = Token(TokenType.START, '', self.get_linum())

        while c: # done when hit TokenType.EOF
            if token.ttype == TokenType.START:
                token.value = c
                # word = c
                if c.isalpha():
                    token.ttype =  TokenType.ID
                elif c.isnumeric():
                    token.ttype =  TokenType.CONSTANT
                elif c in self.rel_start:
                    token.ttype =  TokenType.REL_OPERATOR
                elif c in self.arithmetic_operator:
                    token.ttype =  TokenType.ARITHMETIC_OPERATOR
                    # return (token.ttype, word)
                    return token
                elif c in self.separator:
                    token.ttype =  TokenType.SEPARATOR
                    # return (token.ttype, word)
                    return token
                else:
                    c = ''
            else:
                symbols = [TokenType.REL_OPERATOR, TokenType.ASSIGNMENT]

                #handles anything separated by space
                if token.ttype in [TokenType.ID, TokenType.CONSTANT]:
                    if not c.isalnum():
                        if token.value in self.keyword:
                            token.ttype =  TokenType.KEYWORD

                        if c.isspace():
                            return token
                        else:
                            self.back();
                            return token
                    else:
                        if token.ttype == TokenType.ID and c.isnumeric():
                            msg = "ID cannot contain numbers"
                            msg += f": {token.value} + '{c}'"
                            raise Exception(msg)
                        elif token.ttype == TokenType.CONSTANT and c.isalpha():
                            msg = "Constant cannot contain alphabet"
                            msg += f": {token.value} + '{c}'"
                            raise Exception(msg)
                        else:
                            token.value += c
                else: # either assignment or relation operator
                    if c.isspace():
                        if token.value == '=':
                            token.ttype =  TokenType.ASSIGNMENT

                        return token
                    elif c.isalnum() or c in self.separator:
                        if token.value == '=':
                            token.ttype =  TokenType.ASSIGNMENT

                        self.back();
                        return token
                    else:
                        token.value += c

                # # either a symbol or a white space
                # if token.ttype in [TokenType.ID, TokenType.CONSTANT] \
                #    and not c.isnumeric() \
                #    and not c.isalpha():

                #     if word in self.keyword:
                #         token.ttype =  TokenType.KEYWORD

                #     # either keyword, ID or constant
                #     return token

                #     # if word != '=':
                #     #     self.back()
                #     #     printtoken
                #     #     return token
                #     # else:
                #     #     return (TokenType.ASSIGNMENT, word)

                #     token.ttype =  TokenType.START
                # else:
                #     word +=c

            c = self.next_char()

class FileScanner(Scanner):
    def __init__(self, filename: str):
        self.filename = filename
        self.linum = -1
        self.charpos = 0
        self.isnext = False
        super().__init__()

    def spit(self):
        for line in self.lines:
            print(line)

    def __enter__(self) -> Scanner:
        with open(self.filename) as f:
            self.lines = [x for x in f]

        if len(self.lines) > 0:
            self.linum = 0
            self.charpos = 0
            self.isnext = True

        return self

    def __exit__(self, exc_type, exc_value, tb):
        pass

    def get_linum(self)-> int:
        return self.linum + 1

    def is_next(self):
        return self.isnext

        # pos = self.f.tell()
        # next = False
        # try:
        #     next = True if self.f.read(1) else False
        # finally:
        #     self.f.seek(pos)
        #     return next

    def back(self):
        if self.charpos != 0:
            self.charpos -= 1
        else:
            self.linum -= 1
            self.charpos = len(self.lines[self.linum]) - 1

    def next_char(self):
        if not self.isnext:
            return False

        char = self.lines[self.linum][self.charpos]
        self.charpos += 1

        # if charpos in the end of line
        if self.charpos == len(self.lines[self.linum]):
            # if its the last line
            if self.linum == len(self.lines) - 1:
                self.isnext = False
            else:
                self.linum += 1
                self.charpos = 0
                self.isnext = True
        else:
            self.isnext = True

        return char

class TextScanner(Scanner):
    def __init__(self, text: str):
        self.text = text + "\n"
        self.pointer = 0
        super().__init__()

    def spit(self):
        print(self.text)

    def __enter__(self):
        self.pointer = 0
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.pointer = len(self.text) - 1

    def is_next(self):
        return len(self.text) - 1 >= self.pointer

    def get_linum(self) -> int:
        return 1

    def back(self):
        self.pointer -= 1

    def next_char(self):
        if self.pointer < len(self.text):
            x = deepcopy(self.text[self.pointer])
            self.pointer += 1
            return x
