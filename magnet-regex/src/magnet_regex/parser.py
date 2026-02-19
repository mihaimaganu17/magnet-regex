from lexer import Token, TokenType
from ast_node import *

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        # Cursor for the tokens list
        self.pos = 0
        # Keep track of the number of capture groups
        self.group_counter = 0

    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        # If we consumed all the tokens, keep returning the last one 
        return self.tokens[-1]

    def advance(self) -> Token:
        """Return the token at the current position and go to the next one"""
        token = self.current_token()
        if self.pos < len(self.tokens):
            self.pos += 1 
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Consume token of an expected type or raise an error"""
        token = self.current_token()

        if token.t_type != token_type:
            raise ValueError(
                f"Expected {token_type}, got {token.t_type} at position {token.position}"
            )
        return self.advance()