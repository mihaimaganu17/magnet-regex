import unittest
from magnet_regex.lexer import Lexer, Token, TokenType

class TestLexer(unittest.TestCase):
    def test_tokenise_backref(self):
        lexer = Lexer(r"This: \1\2 is a backref \123 test")
        tokens = lexer.tokenize()

        self.assertEqual(
            tokens,
            [
                Token(TokenType.BACKREF, r"\1", 6),
                Token(TokenType.BACKREF, r"\2", 8),
                Token(TokenType.BACKREF, r"\123", 24),
            ]
        )