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

    def parse(self) -> ASTNode:
        """Recusively parses the regex, from the lowest preceding operator (parse_alteration) to 
        to highest preceding one (parsing_atoms). Through this, we honor the grammar, by processing
        / instantiating the atom first and """
        self.parse_alternation()

    def parse_alternation(self) -> ASTNode:
        self.parse_concat()

    def parse_concat(self) -> ASTNode:
        items = []

        while True:
            token = self.current_token()

            if token.t_type in {TokenType.PIPE, TokenType.RPAREN, TokenType.EOF}:
                break

            # This if checks for a literal dash outside a sequence ([a-z]) or for a literal comma
            # outside a quantifier ({1, 2})
            if token.t_type in {TokenType.DASH, TokenType.COMMA}:
                self.advance()
                items.append(CharNode(token.value))
                continue

            self.parse_quantified()

        return ConcatNode(items)

    def parse_quantified(self) -> ASTNode:
        self.parse_atom()

    def parse_atom(self) -> ASTNode:
        token = self.current_token()

        if token.t_type == TokenType.CHAR:
            self.advance()
            return CharNode(token.value)
        elif token.t_type == TokenType.DOT:
            self.advance()
            return DotNode()
        elif token.t_type == TokenType.CARET:
            self.advance()
            return AnchorNode("^")
        elif token.t_type == TokenType.DOLLAR:
            self.advance()
            return AnchorNode("$")
        elif token.t_type == TokenType.WORD_BOUNDARY:
            self.advance()
            return AnchorNode("b")
        elif token.t_type == TokenType.NON_WORD_BOUNDARY:
            self.advance()
            return AnchorNode("B")