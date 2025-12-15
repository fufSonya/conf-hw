import unittest

from config_translator import translate
from config_translator.errors import EvalError, LexError, ParseError


class TestConstructs(unittest.TestCase):
    def test_number_as_root(self):
        self.assertEqual(translate("123"), "value = 123\n")

    def test_empty_array(self):
        self.assertEqual(translate("#()"), "value = []\n")

    def test_array_of_numbers(self):
        self.assertEqual(translate("#(1, 2, 3)"), "value = [1, 2, 3]\n")

    def test_empty_dict(self):
        self.assertEqual(translate("{}"), "\n")

    def test_simple_dict(self):
        src = "{ a => 1, b => 2 }"
        self.assertEqual(translate(src), "a = 1\nb = 2\n")

    def test_nested_dict_tables(self):
        src = "{ app => { port => 8080, workers => 4 }, debug => 0 }"
        expected = "debug = 0\n\n[app]\nport = 8080\nworkers = 4\n"
        self.assertEqual(translate(src), expected)

    def test_nested_arrays(self):
        src = "#(#(1,2), #(3,4))"
        self.assertEqual(translate(src), "value = [[1, 2], [3, 4]]\n")

    def test_constant_decl_and_use(self):
        src = "10 -> ten { a => [ten], b => #( [ten], 20 ) }"
        expected = "a = 10\nb = [10, 20]\n"
        self.assertEqual(translate(src), expected)

    def test_constant_can_be_dict(self):
        src = "{ x => 1 } -> base { base => [base] }"
        expected = "[base]\nx = 1\n"
        self.assertEqual(translate(src), expected)

    def test_array_of_tables(self):
        src = "{ servers => #({port=>80},{port=>443}) }"
        expected = "[[servers]]\nport = 80\n\n[[servers]]\nport = 443\n"
        self.assertEqual(translate(src), expected)


class TestErrors(unittest.TestCase):
    def test_lex_error(self):
        with self.assertRaises(LexError):
            translate("@")

    def test_parse_error_missing_brace(self):
        with self.assertRaises(ParseError):
            translate("{ a => 1 ")

    def test_parse_error_unexpected_after_final_expr(self):
        with self.assertRaises(ParseError):
            translate("1 2")

    def test_eval_error_undefined_constant(self):
        with self.assertRaises(EvalError):
            translate("{ a => [missing] }")

    def test_eval_error_mixed_array_types(self):
        with self.assertRaises(EvalError):
            translate("#(1, {a=>2})")


if __name__ == "__main__":
    unittest.main()

