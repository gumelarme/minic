from minic.parser import Parser
from minic.scanner import FileScanner
from minic.symboltable import SymbolTable, TypeSymbol, VarSymbol
from minic.node import NodeVisitor

if __name__ == '__main__':
    # symtab = SymbolTable()
    # double = TypeSymbol('double')
    # symtab.insert(double)
    # symtab.insert(VarSymbol('y', double))
    # print(symtab)

    with FileScanner('./examples/example10-1.c') as scan:
        # scan.spit()
        # while scan.is_next():
        #     print(scan.next_token())
        print(scan.spit())
        ast = Parser(scan).start()
        print(ast)
        # nv = NodeVisitor(ast)
        # nv.start()

