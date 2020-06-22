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
        return "<{classname}(name:'{name}')>".format(
            classname= self.__class__.__name__,
            name=self.name
        )

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
    params: List[VarSymbol]

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

class ParamSymbol(Symbol):
    pass


class SymbolTable:
    _table: Dict

    def __init__(self):
        """Init including creation of basic types"""
        self._table = {}
        self.insert(TypeSymbol('int'))
        self.insert(TypeSymbol('void'))
        self.insert(TypeSymbol('bool'))

    def insert(self, sym: Symbol):
        self._table[sym.name] = sym

    def lookup(self, name:str) -> Symbol:
        return self._table[name]

    def __str__(self):
        max_type = max([len(x) for x in self._table.keys()])
        fmt = "{:<%d}: {}" % max_type
        content = [fmt.format(k, v) for k, v in self._table.items()]
        return "\n".join(content)
