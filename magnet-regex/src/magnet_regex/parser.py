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
        / instantiating the atom first and"""
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
        elif token.t_type == TokenType.DIGIT:
            self.advance()
            return PredefinedClassNode("d")
        elif token.t_type == TokenType.NON_DIGIT:
            self.advance()
            return PredefinedClassNode("D")
        elif token.t_type == TokenType.WORD:
            self.advance()
            return PredefinedClassNode("w")
        elif token.t_type == TokenType.NON_WORD:
            self.advance()
            return PredefinedClassNode("W")
        elif token.t_type == TokenType.WHITESPACE:
            self.advance()
            return PredefinedClassNode("s")
        elif token.t_type == TokenType.NON_WHITESPACE:
            self.advance()
            return PredefinedClassNode("S")
        elif token.t_type == TokenType.BACKREF:
            self.advance()
            return BackreferenceNode(int(token.value))
        elif token.t_type == TokenType.LBRACKET:
            # We have a charcter class
            return self._parse_char_class()
        elif token.t_type == TokenType.LPAREN:
            # We have a group
            return self._parse_group()
        elif token.t_type == TokenType.NON_CAPTURING:
            return self._parse_non_capturing_group()
        elif token.t_type == TokenType.LOOKAHEAD_POS:
            return self._parse_lookahead(positive=True)
        elif token.t_type == TokenType.LOOKAHEAD_NEG:
            return self._parse_lookahead(positive=False)


    def _parse_char_class(self) -> CharClassNode:
        self.expect(TokenType.LBRACKET)

        # Check if the character class is negated through caret
        negated = False
        if self.current_token().t_type == TokenType.CARET:
            negated = True
            self.advance()

        chars = set()

        while self.current_token().t_type != TokenType.RBRACKET:
            token = self.current_token()

            # If we reached the last token and we still miss the right bracket, this is an error
            if token.t_type == TokenType.EOF:
                raise ValueError("Unclosed character class")

            if token.type == TokenType.CHAR:
                char = token.value
                self.advance()

                # check if we have a range
                if self.current_token().t_type == TokenType.DASH:
                    next_token = self.peek_token()
                    # If we have a range of character
                    if next_token.t_type == TokenType.CHAR:
                        self.advance()
                        end_char = self.current_token().value
                        self.advance()

                        # We add each character in that range into the set
                        start_ord = ord(char)
                        end_ord = ord(end_char)

                        # Check if the range is valid
                        if start_ord > end_ord:
                            raise ValueError(
                                f"Invalid range {char}-{end_char}: start > end"
                            )
                        if start_ord < 0 or start_ord > 255:
                            raise ValueError(f"Invalid ASCII {char} -> {start_ord}")
                        if end_ord < 0 or end_ord > 255:
                            raise ValueError(f"Invalid ASCII {end_char} -> {end_ord}")

                        for code in range(start_ord, end_ord + 1):
                            chars.add(chr(code))
                    else:
                        # We treat both the character and the dash `-` as  literals
                        chars.add(char)
                        chars.add("-")
                else:
                    # If there is no dash afterwards, we add the character to the set
                    chars.add(char)
            elif token.t_type == TokenType.DIGIT:
                self.advance()
                chars.update("0123456789")
            elif token.t_type == TokenType.WORD:
                self.advance()
                lowercase_letters = [
                    "".join([chr(l) for l in range(ord("a"), ord("z") + 1)])
                ]
                uppercase_letters = [
                    "".join([chr(l) for l in range(ord("A"), ord("Z") + 1)])
                ]
                chars.update(lowercase_letters + uppercase_letters + ["0123456789_"])
            elif token.t_type == TokenType.WHITESPACE:
                self.advance()
                chars.update(" \t\n\r\f\v")
            elif token.t_type == TokenType.DASH:
                self.advance()
                chars.add("-")
            # Inside a character calls, all these are literals
            elif token.t_type in (
                TokenType.PLUS,
                TokenType.STAR,
                TokenType.QUESTION,
                TokenType.DOT,
                TokenType.PIPE,
                TokenType.CARET,
                TokenType.DOLLAR,
                TokenType.LBRACE,
                TokenType.RBRACE,
                TokenType.LPAREN,
                TokenType.RPAREN,
            ):
                self.advance()
                chars.add(char)
            else:
                raise ValueError(
                    f"Unexpected token {token.t_type} in character class at position {self.pos}"
                )

        self.expect(TokenType.RBRACKET)

        if not chars:
            raise ValueError("Empty character class")
        return CharClassNode(chars, negated)

    def _parse_group(self) -> GroupNode:
        self.expect(TokenType.LPAREN)

        self.group_counter += 1
        group_num = self.group_counter

        # You can have any regex in a capturing group
        child = self.parse_alternation()

        self.expect(TokenType.RPAREN)

        return GroupNode(child, group_num)


    def _parse_non_capturing_group(self) -> NonCapturingGroupNode:
        self.advance()
        child = self.parse_alternation()
        self.expect(TokenType.RPAREN)
        return NonCapturingGroupNode(child)

    def _parse_lookahead(self, positive: bool) -> LookaheadNode:
        self.advance()
        child = self.parse_alternation()
        self.expect(TokenType.RPAREN)
        return LookaheadNode(child, positive)


    def expect(self, expected: TokenType) -> Token:
        token = self.current_token()
        if token.t_type != expected:
            raise ValueError(
                f"Expected {expected}, got {token.t_type} at position {token.position}"
            )
        return self.advance()

    def peek_token(self, offset: int = 1) -> Token:
        offset_pos = self.pos + offset
        if offset >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[offset_pos]
