import pytest
from minic.node import Node

class TestNode:
    def test_get_tree_recurse(self):
        op_return = Node(1, ['return', 1])
        op_if = Node(1, ['if ', ['>', 'n', 3],
                              ['body', op_return]])

        assert op_if.get_tree() == ['if ', ['>', 'n', 3],
                              ['body', ['return', 1]]]

    def test_get_tree_recurse_else(self):
        op_return = Node(1, ['return', 1])
        op_return2 = Node(1, ['return', 0])

        op_if = Node(1, ['if ', ['>', 'n', 3],
                              ['body', op_return],
                              ['else', op_return2]])

        assert op_if.get_tree() == ['if ', ['>', 'n', 3],
                                    ['body', ['return', 1]],
                                    ['else', ['return', 0]]]
