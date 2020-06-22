import pytest
from minic.parser import Parser
from minic.scanner import TextScanner
from minic.node import Node
from random import randint

class TestMyParser:
    def teardown_method(self, method):
        self.scan.close()
        self.scan, self.text, self.parser = [None]*3

    def _settext(self, text: str):
        self.scan = TextScanner(text).open()
        self.parser = Parser(self.scan)

    def _parse_from(self, method):
        return self.parser.start(startfrom=method)

    def _exec(self, text, method):
        self._settext(str(text))
        result = self._parse_from(method)
        return result == text

    def _getrandom(self):
        return randint(0, 1000)

    def _op(self, val):
        return Node(1, val)
    # declaration_list
    # type_declaration
    # var_declaration
    def test_var_declaration_int(self):
        self._settext('int varname;')
        assert self._parse_from('var_declaration') == self._op(['var', 'int', 'varname'])
    # function_declaration
    # parameter_list
    def test_parameter_list_one(self):
        self._settext('int x')
        expected = ['params', ['int', 'x']]
        assert self._parse_from('parameter_list') == expected

    def test_parameter_list_void(self):
        self._settext('void')
        expected = ['params', ['void']]
        assert self._parse_from('parameter_list') == expected

    def test_parameter_list_void_int(self):
        self._settext('void, int x')
        expected = ['params', ['void']]
        assert self._parse_from('parameter_list') == expected

    def test_parameter_list_multiple(self):
        self._settext('int x, int i, int j')
        expected = ['params', ['int', 'x'], ['int', 'i'], ['int', 'j']]
        assert self._parse_from('parameter_list') == expected

    # parameter
    # type_specifier
    def test_type_specifier(self):
        text = ["int", "void"]
        result = [self._exec(x, "type_specifier") for x in text]
        assert len(result) == sum(result)

    # statement
    # compound_stmt
    # iteration_stmt
    # selection_stmt
    def test_selection_stmt_if_oneliner(self):
        exp = "if(n > 3) return; "
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if', ['>', 'n', 3], ['body', ['return']]]

    def test_selection_stmt_ifelse_oneliner(self):
        exp = "if(n > 3) return 1; else return 0;"
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if', ['>', 'n', 3], ['body', ['return', 1]], ['else', ['return', 0]]]

    def test_selection_stmt_if_single_stmt(self):
        exp = """
if(n > 3)
    return;
        """
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if', ['>', 'n', 3], ['body', ['return']]]

    def test_selection_stmt_ifelse_single_stmt(self):
        exp = """
if(n > 3)
    return 1;
else
    return 0;
        """
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if', ['>', 'n', 3], ['body', ['return', 1]], ['else', ['return', 0]]]

    def test_selection_stmt_if_compound_stmt(self):
        exp = """
if(n > 3){
    x = n * 2;
    return x;
}
        """
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if',
                          ['>', 'n', 3],
                          ['body',
                           ['=', 'x', ['*', 'n', 2]],
                           ['return', 'x']
                          ]]
    def test_selection_stmt_ifelse_compound_stmt(self):
        exp = """
if(n > 3){
    x = n * 2;
    return x;
}else{
    x = n + 1;
    return x;
}
        """
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if',
                          ['>', 'n', 3],
                          ['body',
                           ['=', 'x', ['*', 'n', 2]],
                           ['return', 'x']],
                          ['else',
                           ['=', 'x', ['+', 'n', 1]],
                           ['return', 'x']]]
    def test_selection_stmt_if_compound_empty(self):
        exp = """
if(n > 3){
}
        """
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if',
                          ['>', 'n', 3],
                          ['body']]
    def test_selection_stmt_ifelse_compound_empty(self):
        exp = """
if(n > 3){
}else{
}
        """
        self._settext(exp)
        result = self._parse_from("statement").get_tree()
        assert result == ['if', ['>', 'n', 3], ['body'], ['else']]

    # jump_stmt
    def test_jump_stmt_return(self):
        text = "return 9;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['return', 9]

    def test_jump_stmt_return_zero(self):
        text = "return 0;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['return', 0]

    def test_jump_stmt_return_var(self):
        text = "return nicething;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['return', 'nicething']
    def test_jump_stmt_return_arithmetic(self):
        text = "return 2 + 9;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['return', ['+', 2, 9]]

    def test_jump_stmt_return_bool1(self):
        text = "return 2 == 9;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['return', ['==', 2, 9]]

    def test_jump_stmt_return_bool2(self):
        text = "return 2 < 9;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['return', ['<', 2, 9]]

    def test_jump_stmt_break(self):
        text = "break;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['break']

    def test_jump_stmt_goto(self):
        text = "goto SOMETHING;"
        self._settext(text)
        result = self._parse_from("jump_stmt")
        assert result == ['goto', 'SOMETHING']

    # exp_stmt
    # labeled_stmt
    # def test_labeled_stmt_label_oneliner(self):
    #     self._settext("DOSOMETHING: nice()")
    #     result = self._parse_from("labeled_stmt")

    # optional expression
    # exp
    # assignment_exp
    def test_assignment_exp_var(self):
        self._settext("something = 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', 3]
        assert result == expect

    def test_assignment_exp_arr(self):
        self._settext("something[0] = 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something[0]', 3]
        assert result == expect

    def test_assignment_exp_obj(self):
        self._settext("something.val = 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something.val', 3]
        assert result == expect

    def test_assignment_exp_add_exp(self):
        self._settext("something = 3 + 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['+', 3, 3]]
        assert result == expect

    def test_assignment_exp_add_exp_mul_chained(self):
        self._settext("something = 3 + 3 * 4")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['+', 3, ['*', 3, 4]]]
        assert result == expect

    def test_assignment_exp_chained(self):
        self._settext("something = nice = 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['=', 'nice', 3]]
        assert result == expect

    def test_assignment_exp_arithmetic1(self):
        self._settext("something = nice + 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['+', 'nice', 3]]
        assert result == expect

    def test_assignment_exp_arithmetic2(self):
        self._settext("something = nice + 3 * some")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['+', 'nice', ['*', 3, 'some']]]
        assert result == expect

    def test_assignment_exp_bool_exp1(self):
        self._settext("something = nice == 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['==', 'nice', 3]]
        assert result == expect

    def test_assignment_exp_bool_exp2(self):
        self._settext("something = nice < 3")
        result = self._parse_from('assignment_exp')
        expect = ['=', 'something', ['<', 'nice', 3]]
        assert result == expect


    # variable
    def test_variable_var(self):
        varname = 'something'
        self._settext(varname)
        assert self._parse_from('variable') == varname

    def test_variable_arr(self):
        varname = 'something[100]'
        self._settext(varname)
        assert self._parse_from('variable') == varname

    def test_variable_object(self):
        varname = 'something.value'
        self._settext(varname)
        assert self._parse_from('variable') == varname


    # call_function
    def test_call_function_no_args(self):
        self._settext("x()")
        result = self._parse_from("call_function")
        assert result == ['call-func', 'x', ['args']]

    def test_call_function_args(self):
        self._settext("x(2+3, 4)")
        result = self._parse_from("call_function")
        assert result == ['call-func', 'x', ['args', ['+', 2, 3], 4]]

    def test_call_function_args_call_function(self):
        self._settext("x(2+3, x(3, 2))")
        result = self._parse_from("call_function")
        assert result == ['call-func', 'x', ['args', ['+', 2, 3], ['call-func', 'x', ['args', 3, 2]]]]


    # argument_list
    def test_argument_list_noargs(self):
        self._settext(')')
        result = self._parse_from('argument_list')
        assert result == ['args']

    def test_argument_list_single_simple(self):
        self._settext('10)')
        result = self._parse_from('argument_list')
        assert result == ['args', 10]

    def test_argument_list_single_complex(self):
        self._settext('10+3/4+nice())')
        result = self._parse_from('argument_list')
        assert result == ['args', ['+', ['+', 10, ['/', 3, 4]], ['call-func', 'nice', ['args']]]]

    def test_argument_list_multiple_simple(self):
        self._settext('3, 10, 90, 99, 18)')
        result = self._parse_from('argument_list')
        assert result == ['args', 3, 10, 90, 99, 18]

    def test_argument_list_multiple_complex(self):
        self._settext('x(), nice + 3, n > 10)')
        result = self._parse_from('argument_list')
        assert result == ['args', ['call-func', 'x', ['args']], ['+', 'nice', 3], ['>', 'n', 10]]


    # conditional_exp
    def test_conditional_exp(self):
        self._settext("nice > 10")
        result = self._parse_from("conditional_exp")
        assert result == ['>', 'nice', 10]

    def test_conditional_every_operator(self):
        rel_operator = ['<', '>', '>=', '<=', '==', '!=']
        a, b = 'somevar', 3
        expressions = [f"{a} {x} {b}" for x in rel_operator]
        expected_results = [[x, a, b] for x in rel_operator]

        results = []
        for i, x in enumerate(expressions):
            self._settext(x)
            results += [self._parse_from('conditional_exp') == expected_results[i]]

        assert sum(results) == len(results)

    def test_conditional_exp_chained(self):
        self._settext("nice > 10 == 3")
        result = self._parse_from("conditional_exp")
        assert result == ['==', ['>', 'nice', 10], 3]

    def test_conditional_exp_complex(self):
        self._settext("nice > 10 == (3 + 3) * 7")
        result = self._parse_from("conditional_exp")
        assert result == ['==', ['>', 'nice', 10], ['*', ['+', 3, 3], 7]]


    # add_exp
    def test_add_exp_num_num(self):
        a, b= self._getrandom(), self._getrandom()
        self._settext(f"{a} + {b}")
        result = self._parse_from("add_exp")
        assert ['+', a, b] == result

    def test_add_exp_var_num(self):
        a, b= 'somevar', self._getrandom()
        self._settext(f"{a} + {b}")
        result = self._parse_from("add_exp")
        assert ['+', a, b] == result

    def test_add_exp_num_chained(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} + {b} + {c}")
        result = self._parse_from("add_exp")
        assert ['+', ['+', a, b], c] == result

    def test_add_exp_sub_num_num(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} - {b}")
        result = self._parse_from("add_exp")
        assert ['-', a, b] == result

    def test_add_exp_sub_num_chained(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} - {b} - {c}")
        result = self._parse_from("add_exp")
        assert ['-', ['-', a, b], c] == result

    def test_add_exp_plussub_num_chained(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} + {b} - {c}")
        result = self._parse_from("add_exp")
        assert ['-', ['+', a, b], c] == result

    def test_add_exp_plusmul_num(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} + {b} * {c}")
        result = self._parse_from("add_exp")
        assert ['+', a, ['*', b, c]] == result

    def test_add_exp_mulplus_num(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} * {b} + {c}")
        result = self._parse_from("add_exp")
        assert ['+', ['*', a, b], c] == result

    def test_add_exp_mul_only(self):
        a, b = self._getrandom(), self._getrandom()
        self._settext(f"{a} * {b}")
        result = self._parse_from("add_exp")
        assert ['*', a, b] == result

    def test_add_exp_mul_only_chained(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"{a} * {b} * {c}")
        result = self._parse_from("add_exp")
        assert ['*', ['*', a, b], c] == result

    def test_add_exp_plus_parens_mul(self):
        a, b, c = self._getrandom(), self._getrandom(), self._getrandom()
        self._settext(f"({a} + {b}) * {c}")
        result = self._parse_from("add_exp")
        assert ['*', ['+', a, b], c] == result


    # multi_exp
    def test_multi_exp_num_num(self):
        a, b= self._getrandom(), self._getrandom()
        self._settext(f"{a} * {b}")
        result = self._parse_from("multi_exp")
        assert ['*', a, b] == result

    def test_multi_exp_var_num(self):
        a, b= 'somevar', self._getrandom()
        self._settext(f"{a} * {b}")
        result = self._parse_from("multi_exp")
        assert ['*', a, b] == result

    def test_multi_exp_num_chained(self):
        a, b, c= self._getrandom(), self._getrandom() , self._getrandom()
        self._settext(f"{a} * {b} * {c}")
        result = self._parse_from("multi_exp")
        assert ['*', ['*', a, b], c] == result

    def test_multi_exp_var_num_num(self):
        a, b, c= 'somevar', self._getrandom() , self._getrandom()
        self._settext(f"{a} * {b} * {c}")
        result = self._parse_from("multi_exp")
        assert ['*', ['*', a, b], c] == result

    def test_multi_exp_div_num_num(self):
        a, b= self._getrandom(), self._getrandom()
        self._settext(f"{a} / {b}")
        result = self._parse_from("multi_exp")
        assert ['/', a, b] == result

    def test_multi_exp_div_var_num(self):
        a, b= 'somevar', self._getrandom()
        self._settext(f"{a} / {b}")
        result = self._parse_from("multi_exp")
        assert ['/', a, b] == result

    def test_multi_exp_div_num_chained(self):
        a, b, c= self._getrandom(), self._getrandom() , self._getrandom()
        self._settext(f"{a} / {b} * {c}")
        result = self._parse_from("multi_exp")
        assert ['*', ['/', a, b], c] == result

    def test_multi_exp_div_var_num_num(self):
        a, b, c= 'somevar', self._getrandom() , self._getrandom()
        self._settext(f"{a} / {b} * {c}")
        result = self._parse_from("multi_exp")
        assert ['*', ['/', a, b], c] == result

    def test_multi_exp_parens_num_num(self):
        a, b = self._getrandom() , self._getrandom()
        self._settext(f"({a} / {b})")
        result = self._parse_from("multi_exp")
        assert ['/', a, b] == result

    def test_multi_exp_parens_back_num_num_num(self):
        a, b, c=  self._getrandom(), self._getrandom() , self._getrandom()
        self._settext(f"{a} * ({b} * {c})")
        result = self._parse_from("multi_exp")
        assert ['*', a, ['*', b, c]] == result


    # pri_exp
    def test_pri_exp_num(self):
        numbers = [12, 323, 9912, 98874, 128311, 9932347]
        results = [self._exec(x, "pri_exp") for x in numbers]
        assert sum(results) == len(results)

    def test_pri_exp_num_10_zeros(self):
        self._settext("0000000000")
        result = self._parse_from("pri_exp")
        assert result == 0

    def test_pri_exp_num_random(self):
        val = self._getrandom()
        self._settext(str(val))
        result = self._parse_from("pri_exp")
        assert result == val

    def test_pri_exp_parens_single_number(self):
        self._settext("(9213)")
        result = self._parse_from("pri_exp")
        assert result == 9213

    def test_pri_exp_variable(self):
        self._settext("something")
        result = self._parse_from("pri_exp")
        assert result == 'something'

    def test_pri_exp_parens_variable(self):
        self._settext("(somevar)")
        result = self._parse_from("pri_exp")
        assert result == 'somevar'

    def test_pri_exp_parens_variable_array(self):
        self._settext("(somevar[19])")
        result = self._parse_from("pri_exp")
        assert result == 'somevar[19]'

    def test_pri_exp_parens_variable_obj(self):
        self._settext("(somevar.value)")
        result = self._parse_from("pri_exp")
        assert result == 'somevar.value'
