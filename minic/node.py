from dataclasses import dataclass
from typing import List

@dataclass
class Node:
    linum: int
    name: str
    op: List

    def __init__(self, linum, op, name=None):
        self.linum = linum
        self.name = op[0]
        self.op = op

    def get_tree(self):
        result = []
        for x in self.op:
            if type(x) == Node:
                result += [x.get_tree()]
            elif type(x) == list:
                result.append([v.get_tree() if type(v) == Node else v for v in x])
            else:
                result += [x]

        return result

    def get_tree_str(self):
        return str(self.get_tree()).replace("'", "").replace(",", "")


# Example
# op1 = Operation(1, ['+', 'niceVar', 3])
# op3 = Operation(1, ['==', 2, op1])

# print(op3.get_tree_str())
