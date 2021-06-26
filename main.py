from minic.parser import Parser
from minic.scanner import FileScanner
from minic.symboltable import ScopedSymbolTable, TypeSymbol, VarSymbol
from minic.nodevisitor import NodeVisitor

if __name__ == '__main__':
    # symtab = ScopedSymbolTable()
    # double = TypeSymbol('double')
    # symtab.insert(double)
    # symtab.insert(VarSymbol('y', double))
    # print(symtab)

    filepath = './examples/example10-1.c'
    with FileScanner(filepath) as scan:
        print(scan.spit())
        ast = Parser(scan).start()
        nv = NodeVisitor(ast)
        nv.start()
