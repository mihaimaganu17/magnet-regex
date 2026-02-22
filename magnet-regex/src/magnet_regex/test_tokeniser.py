import unittest
from magnet_regex.lexer import Lexer
from magnet_regex.parser import Parser


class TestParser(unittest.TestCase):
    def test_parser(self):
        lexer = Lexer(r"Backref \1\2 test")
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        print(parser.tokens)