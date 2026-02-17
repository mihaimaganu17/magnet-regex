import unittest
from magnet_regex.lexer import Lexer, Token, TokenType

class TestLexer(unittest.TestCase):
    def test_tokenise_backref(self):
        lexer = Lexer(r"Backref \1\2 test")
        tokens = lexer.tokenize()

        self.assertEqual(
            tokens,
            [
                Token(TokenType.CHAR, r"B", 0),
                Token(TokenType.CHAR, r"a", 1),
                Token(TokenType.CHAR, r"c", 2),
                Token(TokenType.CHAR, r"k", 3),
                Token(TokenType.CHAR, r"r", 4),
                Token(TokenType.CHAR, r"e", 5),
                Token(TokenType.CHAR, r"f", 6),
                Token(TokenType.CHAR, r" ", 7),
                Token(TokenType.BACKREF, r"\1", 8),
                Token(TokenType.BACKREF, r"\2", 10),
                Token(TokenType.CHAR, r" ", 12),
                Token(TokenType.CHAR, r"t", 13),
                Token(TokenType.CHAR, r"e", 14),
                Token(TokenType.CHAR, r"s", 15),
                Token(TokenType.CHAR, r"t", 16),
                Token(TokenType.EOF, None, 17),
            ]
        )

    def test_demo_pattern(self):
        lexer = Lexer(r"a\d{1}(?:foo|bar)?")
        tokens = lexer.tokenize()

        self.assertEqual(
            tokens,
            [
                Token(TokenType.CHAR, r"a", 0),
                Token(TokenType.DIGIT, r"\d", 1),
                Token(TokenType.LBRACE, r"{", 3),
                Token(TokenType.CHAR, r"1", 4),
                Token(TokenType.RBRACE, r"}", 5),
                Token(TokenType.NON_CAPTURING, r"(?:", 6),
                Token(TokenType.CHAR, r"f", 9),
                Token(TokenType.CHAR, r"o", 10),
                Token(TokenType.CHAR, r"o", 11),
                Token(TokenType.PIPE, r"|", 12),
                Token(TokenType.CHAR, r"b", 13),
                Token(TokenType.CHAR, r"a", 14),
                Token(TokenType.CHAR, r"r", 15),
                Token(TokenType.RPAREN, r")", 16),
                Token(TokenType.QUESTION, r"?", 17),
                Token(TokenType.EOF, None, 18),
            ]
        )