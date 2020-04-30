from minic.parser import Parser
from minic.scanner import FileScanner


if __name__ == '__main__':
    with FileScanner('./examples/example10-1.c') as scan:
        # scan.spit()
        # while scan.is_next():
        #     print(scan.next_token())
        print(scan.spit())
        pt = Parser(scan)
        result = str(pt.start()).replace("'", "").replace(",", "")
        print(result)
