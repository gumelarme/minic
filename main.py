from __future__ import annotations
from minic.parser import Parser
from minic.scanner import FileScanner
from dataclasses import dataclass
from typing import List, Dict

if __name__ == '__main__':
    with FileScanner('./examples/example10-1.c') as scan:
        # scan.spit()
        # while scan.is_next():
        #     print(scan.next_token())
        print(scan.spit())
        ast = Parser(scan).start()
        print(ast)
