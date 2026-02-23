import unittest
from magnet_regex.lexer import Lexer
from magnet_regex.parser import Parser
from magnet_regex.matcher import Matcher


class TestParser(unittest.TestCase):
    def test_parser(self):
        lexer = Lexer(r"Backref \1\2 test")
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        print(parser.tokens)

    def test_parser2(self):
        lexer = Lexer(r"a\d{1}(?:foo|bar)")
        tokens = lexer.tokenize()
        parser = Parser(tokens)

        print(parser.tokens)

    def test_matcher(self):
        lexer = Lexer(r"ab*c|d")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        matcher = Matcher(ast)

        print(matcher.match("abbc"))

    def test_matcher2(self):
        lexer = Lexer(r"hello$")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        matcher = Matcher(ast)

        print(matcher.match("world hello", 6))

    def test_matcher3(self):
        lexer = Lexer(r"hello$")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        matcher = Matcher(ast)

        print(matcher.search("world hello"))