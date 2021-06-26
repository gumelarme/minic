from __future__ import annotations
from typing import List, Dict, Union
from dataclasses import dataclass


@dataclass
class Symbol:
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

@dataclass
class TypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)


    def __repr__(self):
        return f"<T:{self.name}>"
        # return "<{classname}(name:'{name}')>".format(
        #     classname= self.__class__.__name__,
        #     name=self.name
        # )

@dataclass
class VarSymbol(Symbol):
    name: str
    type: TypeSymbol

    def __init__(self, name, type):
        super().__init__(name, type)


    def __repr__(self):
        return "<{classname}(name:'{name}', type:{type})>".format(
            classname=self.__class__.__name__,
            name=self.name,
            type=self.type
        )

class FunctionSymbol(Symbol):
    name: str
    type: TypeSymbol
    params: List[ParamSymbol]

    def __init__(self, name, type, params=None):
        super().__init__(name, type)
        self.params = params

    def __repr__(self):
        return "<{classname}(name:'{name}', type:{type}, params:{params})>".format(
            classname=self.__class__.__name__,
            name=self.name,
            type=self.type,
            params=self.params
        )


class ScopedSymbolTable:
    _table: Dict
    verbose: bool
    name: str
    level: int
    parent_scope: ScopedSymbolTable

    def __init__(self, name, level, parent_scope=None, verbose=True):
        self.verbose = verbose
        self.name = name
        self.level = level
        self.parent_scope = parent_scope
        """Init including creation of basic types"""
        self._table = {}

    def init_builtin(self):
        self.insert(TypeSymbol('int'))
        self.insert(TypeSymbol('void'))
        self.insert(TypeSymbol('bool'))

    def insert(self, sym: Symbol):
        self._table[sym.name] = sym

        if self.verbose:
            print("Insert:", sym.name)

    def lookup(self, name:str, deep=True) -> Symbol:
        if self.verbose:
            print("Lookup:", name, f"@{self.name}")

        symbol = self._table.get(name, None)

        if symbol:
            return symbol

        if self.parent_scope and deep:
            return self.parent_scope.lookup(name)

        return None


    def __str__(self):
        content = []
        if len(self._table):
            max_type = max([len(x) for x in self._table.keys()])
            fmt = "\t{:<%d} : {}" % max_type
            content = [fmt.format(k, v) for k, v in self._table.items()]

        text = "\n\nSCOPED SYMBOL TABLE"
        l = len(text)
        text += f"\n{'='*l}"
        text += "\nScope name: {}"
        text += "\nScope level: {}"
        text += "\nContents:"
        text += f"\n" + '-'*l
        text += "\n{}"
        text += f"\n" + '-'*l
        return text.format(
            self.name,
            self.level,
            "\n".join(content) if len(content) else '\tNone'
        )
