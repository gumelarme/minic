from random import randint
from typing import List

import pytest

import minic.node as nd
from minic.parser import Parser
from minic.scanner import TextScanner
import copy


def _exec(text, method):
    text = str(text) # convert everything to str
    with TextScanner(text) as scan:
        scan = TextScanner(text).open()
        parser = Parser(scan)
        return parser.start(startfrom=method)

def _getrandom():
    return randint(0, 1000)

@pytest.mark.parametrize("inp, exp", [
    ("""
    int x;
    int y;
    """, nd.Program(1, [
        nd.VarDecl(1, 'int', 'x'),
        nd.VarDecl(1, 'int', 'y'),
    ])),

    ("""
    int x;
    int function(void){}
    int y;
    """, nd.Program(1, [
        nd.VarDecl(1, 'int', 'x'),
        nd.FuncDecl(1, 'int', 'function', [nd.ParamDecl(1, 'void', None)], []),
        nd.VarDecl(1, 'int', 'y'),
    ])),
])
def test_program(inp, exp):
    assert exp == _exec(inp, None)

@pytest.mark.parametrize("inp, exp", [
    ("""
    int x;
    int y;
    """, [
        nd.VarDecl(1, 'int', 'x'),
        nd.VarDecl(1, 'int', 'y'),
    ]),

    ("""
    int x;
    int function(void){}
    """, [
        nd.VarDecl(1, 'int', 'x'),
        nd.FuncDecl(1, 'int', 'function', [nd.ParamDecl(1, 'void', None)], []),
    ]),

    ("""
    int x;
    int y;
    int function(void){}
    int main(void){}
    int z;
    """, [
        nd.VarDecl(1, 'int', 'x'),
        nd.VarDecl(1, 'int', 'y'),
        nd.FuncDecl(1, 'int', 'function', [nd.ParamDecl(1, 'void', None)], []),
        nd.FuncDecl(1, 'int', 'main', [nd.ParamDecl(1, 'void', None)], []),
        nd.VarDecl(1, 'int', 'z'),
    ]),

    ("""
    int x;
    int function(void){
    }
    """, [
        nd.VarDecl(1, 'int', 'x'),
        nd.FuncDecl(1, 'int', 'function', [nd.ParamDecl(1, 'void', None)], []),
    ]),

    ("""
    int x;
    int function(void){
        int y;
        y = 10 * x;
        return y;
    }
    """, [
        nd.VarDecl(1, 'int', 'x'),
        nd.FuncDecl(1, 'int', 'function', [nd.ParamDecl(1, 'void', None)], [
            nd.VarDecl(1, 'int', 'y'),
            nd.AssignmentOp(1, nd.Var(1, 'y'), nd.BinOp(1, '*', nd.Num(1, 10), nd.Var(1, 'x'))),
            nd.JumpStmt(1, 'return', nd.Var(1, 'y'))
        ]),
    ]),

    ("""
    int x;
    int function(int y, int z){
        y = z * x;
        return y;
    }
    """, [
        nd.VarDecl(1, 'int', 'x'),
        nd.FuncDecl(1, 'int', 'function', [nd.ParamDecl(1, 'int', 'y'), nd.ParamDecl(1, 'int', 'z')], [
            nd.AssignmentOp(1, nd.Var(1, 'y'), nd.BinOp(1, '*', nd.Var(1, 'z'), nd.Var(1, 'x'))),
            nd.JumpStmt(1, 'return', nd.Var(1, 'y'))
        ]),
    ]),
])
def test_declaration_list(inp, exp):
    assert exp == _exec(inp, 'declaration_list')


@pytest.mark.parametrize("name, param, body, exp", [
    ("int main", "void", ["int x", "x = 90", "return x"],
     nd.FuncDecl(1, 'int', 'main', [nd.ParamDecl(1, 'void', None)], [
         nd.VarDecl(1, 'int', 'x'),
         nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 90)),
         nd.JumpStmt(1, 'return', nd.Var(1, 'x'))
     ]
     )),
    ("void main", "int x, int y", ["int x", "x = 90", "return x"],
     nd.FuncDecl(1, 'void', 'main', [nd.ParamDecl(1, 'int', 'x'), nd.ParamDecl(1, 'int', 'y')], [
         nd.VarDecl(1, 'int', 'x'),
         nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 90)),
         nd.JumpStmt(1, 'return', nd.Var(1, 'x'))
     ]
     ))
])
def test_func_declaration(name, param, body, exp):
    stmt = ";\n".join(body) + ";" if len(body) > 0 else ""
    text = f""" {name}({param}){{
        {stmt}
    }}
    """
    assert exp == _exec(text, 'func_declaration')

@pytest.mark.parametrize("inp, exp", [
    ('void', [nd.ParamDecl(1, 'void', None)]),
    ('int x', [nd.ParamDecl(1, 'int', 'x')]),
    ('int x, int y', [nd.ParamDecl(1, 'int', 'x'), nd.ParamDecl(1, 'int', 'y')]),
    ('int longName, int superLongName', [nd.ParamDecl(1, 'int', 'longName'), nd.ParamDecl(1, 'int', 'superLongName')]),
    ('void, int y', [nd.ParamDecl(1, 'void', None)]),
])
def test_parameter_list(inp, exp):
    assert exp == _exec(inp, 'parameter_list')

@pytest.mark.parametrize("inp, exp", [
    ('int x', nd.ParamDecl(1, 'int', 'x')),
    ('int somevar', nd.ParamDecl(1, 'int', 'somevar')),
    ('int varName', nd.ParamDecl(1, 'int', 'varName')),
    ('void', nd.ParamDecl(1, 'void', None)),
    # ('void something', nd.ParamDecl(1, 'void', None)),
    # ('int varName_something', nd.ParamDecl(1, 'int', 'varName_something')),
])
def test_parameter(inp, exp):
    assert exp == _exec(inp, 'parameter')

@pytest.mark.parametrize("inp, exp", [
    ("int x;", nd.VarDecl(1, 'int', 'x')),
    ("int something;", nd.VarDecl(1, 'int', 'something')),
    ("void something;", nd.VarDecl(1, 'void', 'something')),
])
def test_variable_declaration(inp, exp):
    assert exp == _exec(inp, 'var_declaration')

@pytest.mark.parametrize("inp, exp", [
    ("int", "int"),
    ("void", "void")
])
def test_type_specifier(inp, exp):
    assert exp == _exec(inp, 'type_specifier')

@pytest.mark.parametrize("inp, exp", [
    ([],[]),
    (["x = 1"],
     [
         nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 1)),
     ]),
    (["x = 1", "return 1"],
     [
         nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 1)),
         nd.JumpStmt(1, 'return', nd.Num(1, 1))
     ]),
])
def test_compound_statement(inp, exp):
    stmt = ";\n".join(inp) + ";" if len(inp) > 0 else ""
    text= "{{\n{}\n}}".format(stmt)

    assert exp == _exec(text, "compound_stmt")

@pytest.mark.parametrize("cond, body, exp", [
    ("1", [], nd.WhileLoop(1, nd.Num(1, 1), [])),
    ("1", ["x = x + 1"],
     nd.WhileLoop(1, nd.Num(1, 1),
                  [
                      nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Var(1, 'x'), nd.Num(1, 1)))
                  ]
     )),
    ("1", ["x = x + 1", "return x"],
     nd.WhileLoop(1, nd.Num(1, 1),
                  [
                      nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Var(1, 'x'), nd.Num(1, 1))),
                      nd.JumpStmt(1, 'return',nd.Var(1, 'x'))
                  ]
     )),
    ("0", ["x = x + 1"],
     nd.WhileLoop(1, nd.Num(1, 0),
                  [
                      nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Var(1, 'x'), nd.Num(1, 1)))
                  ]
     )),
    # ("", ["x = x + 1"],
    #  nd.WhileLoop(1, None,
    #               [
    #                   nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Var(1, 'x'), nd.Num(1, 1)))
    #               ]
    #  )),
    ("x > 1", ["x = x + 1"],
     nd.WhileLoop(1,
                  nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Num(1, 1)),
                  [
                      nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Var(1, 'x'), nd.Num(1, 1)))
                  ]
     )),
])
def test_iteration_stmt_while_compound(cond, body, exp):
    bodystr = ";\n".join(body)+";" if len(body) > 0 else ""
    text = """ while({}){{
        {}
    }}
    """.format(cond, bodystr)
    assert exp == _exec(text, "iteration_stmt")

@pytest.mark.parametrize("cond, body, exp", [
    ("1", ["x = x + 1"],
     nd.WhileLoop(1, nd.Num(1, 1),
                  [
                      nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Var(1, 'x'), nd.Num(1, 1)))
                  ]
     )),
    # ("1", [],
    #  nd.WhileLoop(1, nd.Num(1, 1),
    #               [
    #               ]
    #  ))
])
def test_iteration_stmt_while_oneliner(cond, body, exp):
    bodystr = ";\n".join(body)+";" if len(body) > 0 else ""
    text = """ while({}){}""".format(cond, bodystr)
    assert exp == _exec(text, "iteration_stmt")

@pytest.mark.parametrize("header, body, exp", [
    (("", "", ""), ["x = 1"],
     nd.ForLoop(1, nd.ForHeader(None, None, None),
        [
            nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 1))
        ]
    )),
    (("i = 1", "i < 5", "i = i + 1"), ["x = 1"],
     nd.ForLoop(1, nd.ForHeader(
         nd.AssignmentOp(1, nd.Var(1, 'i'), nd.Num(1, 1)),
         nd.RelOp(1, '<', nd.Var(1, 'i'), nd.Num(1, 5)),
         nd.AssignmentOp(1, nd.Var(1, 'i'), nd.BinOp(1, '+', nd.Var(1, 'i'), nd.Num(1, 1)))
        ),
        [
            nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 1))
        ]
    )),

    (("i = 1", "i < 5", "i = i + 1"), ["x = 1", "return x"],
     nd.ForLoop(1, nd.ForHeader(
         nd.AssignmentOp(1, nd.Var(1, 'i'), nd.Num(1, 1)),
         nd.RelOp(1, '<', nd.Var(1, 'i'), nd.Num(1, 5)),
         nd.AssignmentOp(1, nd.Var(1, 'i'), nd.BinOp(1, '+', nd.Var(1, 'i'), nd.Num(1, 1)))
        ),
        [
            nd.AssignmentOp(1, nd.Var(1, 'x'), nd.Num(1, 1)),
            nd.JumpStmt(1, 'return', nd.Var(1, 'x'))
        ]
    )),

    (("i = 1", "i < 5", "i = i + 1"), [],
     nd.ForLoop(1, nd.ForHeader(
         nd.AssignmentOp(1, nd.Var(1, 'i'), nd.Num(1, 1)),
         nd.RelOp(1, '<', nd.Var(1, 'i'), nd.Num(1, 5)),
         nd.AssignmentOp(1, nd.Var(1, 'i'), nd.BinOp(1, '+', nd.Var(1, 'i'), nd.Num(1, 1)))
        ),
    )),
])
def test_iteration_stmt_for(header, body: List, exp):
    header_str = "for({}; {}; {})".format(*header)
    statements = ';\n'.join(body) + ";"
    body_str = """ {{
        {}
    }} """.format(statements if len(body) > 0 else "")
    whole = header_str + body_str
    assert exp == _exec(whole, 'iteration_stmt')


@pytest.mark.parametrize("condition, body, elsebody, exp", [
    ("1", ["return 1"], ["return 2"],
     nd.IfOp(1, nd.Num(1, 1),
             [nd.JumpStmt(1, 'return', nd.Num(1, 1))],
             [nd.JumpStmt(1, 'return', nd.Num(1, 2))],
     )),
    ("x > y", ["x = 2 + 3", "return x"], ["y = 30", "return y"],
     nd.IfOp(1, nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Var(1, 'y')),
             [
                 nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3))),
                 nd.JumpStmt(1, 'return', nd.Var(1, 'x'))
             ],
             [
                 nd.AssignmentOp(1, nd.Var(1, 'y'), nd.Num(1, 30)),
                 nd.JumpStmt(1, 'return', nd.Var(1, 'y'))
             ],
     )),
])
def test_selection_stmt__ifelse_onliner(condition, body, elsebody, exp):
    spread = lambda arr, sep: sep.join(arr) + sep
    bodied = """ if({}){{ {} }}else{{ {} }} """.format(
        condition,
        spread(body, ';\n'),
        spread(elsebody, ';\n')
    )

    assert exp == _exec(bodied, "selection_stmt")

@pytest.mark.parametrize("condition, body, elsebody, exp", [
    ("1", ["return 1"], ["return 2"],
     nd.IfOp(1, nd.Num(1, 1),
             [nd.JumpStmt(1, 'return', nd.Num(1, 1))],
             [nd.JumpStmt(1, 'return', nd.Num(1, 2))],
     )),
    ("x > y", ["x = 2 + 3", "return x"], ["return y"],
     nd.IfOp(1, nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Var(1, 'y')),
             [
                 nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3))),
                 nd.JumpStmt(1, 'return', nd.Var(1, 'x'))
             ],
             [nd.JumpStmt(1, 'return', nd.Var(1, 'y'))],
     )),
])
def test_selection_stmt__ifelse(condition, body, elsebody, exp):
    spread = lambda arr, sep: sep.join(arr) + sep
    oneliner = "if({}) {} else {}".format(condition,
                                          spread([body[0]], ';'),
                                          spread(elsebody, ';'))

    bodied = """
    if({}){{
        {}
    }}else{{
        {}
    }}
    """.format(condition, spread(body, ';\n'), spread(elsebody, ';\n'))

    oneliner_exp = copy.deepcopy(exp)
    oneliner_exp.body = [oneliner_exp.body[0]]
    assert oneliner_exp == _exec(oneliner, "selection_stmt")
    assert exp == _exec(bodied, "selection_stmt")

@pytest.mark.parametrize("condition, body, exp", [
    ("x > 2", ["x=2+3"], nd.IfOp(1, nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Num(1, 2)),
                                 [nd.AssignmentOp(1, nd.Var(1, 'x'),
                                                 nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3)))]
    )),

    ("x > 2", ["return 1"], nd.IfOp(1, nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Num(1, 2)),
                                 [nd.JumpStmt(1, 'return', nd.Num(1, 1))]
    )),

    ("1", ["x=2+3"], nd.IfOp(1, nd.Num(1, 1),
                                 [nd.AssignmentOp(1, nd.Var(1, 'x'),
                                                 nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3)))]
    )),

    ("0", ["x=2+3"], nd.IfOp(1, nd.Num(1, 0),
                                 [nd.AssignmentOp(1, nd.Var(1, 'x'),
                                                 nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3)))]
    )),

    ("x", ["x=2+3"], nd.IfOp(1, nd.Var(1, 'x'),
                                 [nd.AssignmentOp(1, nd.Var(1, 'x'),
                                                 nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3)))]
    )),

    ("x > 2", ["x=2+3", "x = 23 * 3", "return 1"], nd.IfOp(1,
                               nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Num(1, 2)),
                                 [
                                     nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3))),
                                     nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '*', nd.Num(1, 23), nd.Num(1, 3))),
                                     nd.JumpStmt(1, 'return', nd.Num(1, 1))
                                 ]
    )),

    # Nested
    ("x > 2", ["x=2+3", "x = 23 * 3", "if(x > 3) return 1"], nd.IfOp(1,
                               nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Num(1, 2)),
                                 [
                                     nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '+', nd.Num(1, 2), nd.Num(1, 3))),
                                     nd.AssignmentOp(1, nd.Var(1, 'x'), nd.BinOp(1, '*', nd.Num(1, 23), nd.Num(1, 3))),
                                     nd.IfOp(1, nd.RelOp(1, '>', nd.Var(1, 'x'), nd.Num(1, 3)),
                                             [nd.JumpStmt(1, 'return', nd.Num(1, 1))]
                                     )
                                 ]
    )),

])
def test_selection_stmt__if(condition, body, exp):
    spread = lambda arr, sep: sep.join(arr) + sep
    oneliner = f"if({condition}) {spread(body, ';')}"
    bodied = """
    if({}){{
        {}
    }}
    """.format(condition, spread(body, ';\n'))

    oneliner_exp = copy.deepcopy(exp)
    oneliner_exp.body = [oneliner_exp.body[0]]
    # print()
    # print("============================")
    # print(f"{oneliner_exp} \n{exp}")
    assert oneliner_exp == _exec(oneliner, "selection_stmt")
    assert exp == _exec(bodied, "selection_stmt")

@pytest.mark.parametrize("inp, exp", [
    ("return;", nd.JumpStmt(1, 'return')),
    ("return 1;", nd.JumpStmt(1, 'return', nd.Num(1, 1))),
    ("return x;", nd.JumpStmt(1, 'return', nd.Var(1, 'x'))),
    ("return 1+2;", nd.JumpStmt(1, 'return', nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)))),
    ("return nice == 2;", nd.JumpStmt(1, 'return', nd.RelOp(1, '==', nd.Var(1, 'nice'), nd.Num(1, 2)))),
    ("return function();", nd.JumpStmt(1, 'return', nd.CallFuncOp(1, 'function'))),
    ("goto something;", nd.JumpStmt(1, 'goto', 'something')),
    ("break;", nd.JumpStmt(1, 'break')),
])
def test_jump_stmt(inp, exp):
    res = _exec(inp, "jump_stmt")
    assert res == exp

@pytest.mark.parametrize("inp, exp", [
])
def test_exp_stmt(inp, exp):
    pass

@pytest.mark.parametrize("inp, exp", [
])
def test_labeled_exp(inp, exp):
    pass

@pytest.mark.parametrize("inp, exp", [
])
def test_optional_exp(inp, exp):
    pass

@pytest.mark.parametrize("inp, exp", [
])
def test_exp(inp, exp):
    pass

@pytest.mark.parametrize("inp, exp", [
    ("x = 10", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.Num(1, 10))),
    ("x = y", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.Var(1, 'y'))),
    ("x = y = 10", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.AssignmentOp(1, nd.Var(1, 'y'), nd.Num(1, 10)))),
    ("x = y == 10", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.RelOp(1, '==', nd.Var(1, 'y'), nd.Num(1, 10)))),
    ("x = y == z", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.RelOp(1, '==', nd.Var(1, 'y'), nd.Var(1, 'z')))),
    ("x = y + 10", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.BinOp(1, '+', nd.Var(1, 'y'), nd.Num(1, 10)))),
    ("x = y + z", nd.AssignmentOp(1, nd.Var(1,  'x'), nd.BinOp(1, '+', nd.Var(1, 'y'), nd.Var(1, 'z')))),
    ("x = y + z * 10", nd.AssignmentOp(1, nd.Var(1,  'x'),
                                       nd.BinOp(1, '+', nd.Var(1, 'y'),
                                                nd.BinOp(1, '*', nd.Var(1, 'z'), nd.Num(1, 10))))),

    ("x = y = z = 10", nd.AssignmentOp(1, nd.Var(1,  'x'),
                                       nd.AssignmentOp(1, nd.Var(1, 'y'),
                                                       nd.AssignmentOp(1, nd.Var(1, 'z'), nd.Num(1, 10))))),
])
def test_assignment_exp(inp, exp):
    res = _exec(inp, "assignment_exp")
    assert res == exp

@pytest.mark.parametrize("inp, exp", [
    ("var", nd.Var(1, 'var')),
    ("SOMETHING", nd.Var(1, 'SOMETHING')),
    ("var[2]", nd.Var(1, 'var', 2)),
    ("var.height", nd.Var(1, 'var', 'height')),
    # ("int", nd.Var(1, 'int')),
])
def test_variable(inp, exp):
    res = _exec(inp, "variable")
    assert res == exp

@pytest.mark.parametrize("inp, exp", [
    ("f()", nd.CallFuncOp(1, 'f')),
    ("f(1)", nd.CallFuncOp(1, 'f', [nd.Num(1, 1)])),
    ("f(param)", nd.CallFuncOp(1, 'f', [nd.Var(1, 'param')])),
    ("f(g())", nd.CallFuncOp(1, 'f', [nd.CallFuncOp(1, 'g')])),
    ("f(g(1))", nd.CallFuncOp(1, 'f', [nd.CallFuncOp(1, 'g', [nd.Num(1, 1)])])),
    ("f(1, param)", nd.CallFuncOp(1, 'f', [nd.Num(1, 1), nd.Var(1, 'param')])),
    ("f(1 + 2)", nd.CallFuncOp(1, 'f', [nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2))])),
    ("f(1 + 2, 3)", nd.CallFuncOp(1, 'f', [nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3)])),
])
def test_call_function(inp, exp):
    res = _exec(inp, "call_function")
    assert res == exp

@pytest.mark.parametrize("inp, exp", [
    (")", None),
    ("1)", [nd.Num(1, 1)]),
    ("arg)", [nd.Var(1, 'arg')]),
    ("1, 2, arg)", [nd.Num(1, 1), nd.Num(1, 2), nd.Var(1, 'arg')]),
    ("1+2)", [nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2))]),
    ("1+2, 2)", [nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 2)]),
    ("1+2, arg)", [nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Var(1, 'arg')]),
    ("(1+2))", [nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2))]),
    ("(1+2)*3)", [nd.BinOp(1, '*', nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3))]),
])
def test_argument_list(inp, exp):
    res = _exec(inp, "argument_list")
    assert res == exp

@pytest.mark.parametrize("lstr, rstr, lnode, rnode", [
    ('1', '2', nd.Num(1, 1), nd.Num(1, 2)),
    ('1', 'somebool', nd.Num(1, 1), nd.Var(1, 'somebool')),
    ('1+2', '3', nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3)),
])
def test_conditional_exp(lstr, rstr, lnode, rnode):
    op = ['>', '<', '==', '!=', '>=', '<=',]
    join_str = lambda x, y, z: _exec(x + z + y, 'conditional_exp')
    join_node = lambda x, y, z: nd.RelOp(1, z, x, y)

    param = [(join_str(lstr, rstr, o), join_node(lnode, rnode, o))for o in op]
    for x in range(len(op)):
        assert param[x][0] == param[x][1]


@pytest.mark.parametrize("inp, exp", [
    ("1 + 2", nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2))),
    ("1 + 2 - 3", nd.BinOp(1, '-', nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3))),
    ("1 + 2 * 3", nd.BinOp(1, '+', nd.Num(1, 1), nd.BinOp(1, '*', nd.Num(1, 2), nd.Num(1, 3)))),
    ("(1 + 2) * 3", nd.BinOp(1, '*', nd.BinOp(1, '+', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3))),
    ("1 * 2 / 3", nd.BinOp(1, '/', nd.BinOp(1, '*', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3))),
    ("var + 2", nd.BinOp(1, '+', nd.Var(1, 'var'), nd.Num(1, 2))),
])
def test_add_exp(inp, exp):
    res = _exec(inp, "add_exp")
    assert res == exp

@pytest.mark.parametrize("inp, exp", [
    ("1 * 2", nd.BinOp(1, '*', nd.Num(1, 1), nd.Num(1, 2))),
    ("1 * 2 / 3", nd.BinOp(1, '/', nd.BinOp(1, '*', nd.Num(1, 1), nd.Num(1, 2)), nd.Num(1, 3))),
])
def test_multi_exp(inp, exp):
    res = _exec(inp, "multi_exp")
    assert res == exp

# primary exp
def test_pri_exp__func_call_num_args():
    func = "index(1, 2, 4)"
    res = _exec(func, "pri_exp")

    assert res == nd.CallFuncOp(1, 'index', [nd.Num(1, x) for x in [1, 2, 4]])

def test_pri_exp__func_call_no_args():
    func = "index()"
    res = _exec(func, "pri_exp")
    assert res == nd.CallFuncOp(1, 'index')

@pytest.mark.parametrize("var", "x y variable".split(" "))
def test_pri_exp__var(var):
    res = _exec(var, "pri_exp")
    assert res == nd.Var(1, var)

@pytest.mark.parametrize("number", [000, 0, 1, 30, 200, 99, 1000000])
def test_pri_exp__num(number):
    res = _exec(number, "pri_exp")
    assert res == nd.Num(1, number)

@pytest.mark.parametrize("number", [000, 0, 1, 30, 200, 99, 1000000])
def test_pri_exp__num_in_parens(number):
    res = _exec(f"({number})", "pri_exp")
    assert res == nd.Num(1, number)
