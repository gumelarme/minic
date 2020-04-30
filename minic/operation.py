from dataclasses import dataclass
from typing import List

@dataclass
class Operation:
    linum: int
    op: List

    def get_tree(self):
        result = []
        for x in self.op:
            if type(x) == Operation:
                result += [x.get_tree()]
            else:
                result += [x]
        return result

    def get_tree_str(self):
        return str(self.get_tree()).replace("'", "").replace(",", "")


# Example
# op1 = Operation(1, ['+', 'niceVar', 3])
# op3 = Operation(1, ['==', 2, op1])

# print(op3.get_tree_str())
