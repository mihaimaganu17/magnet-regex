from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TokenType(int, Enum):
    """All possible token types in our regex language"""

    # Regular character (A-Z, a-z, 0-9, etc.)
    CHAR = 0
    # (Zero or more of previous construct) -> ab*c: ac, abc, abbc, abbbc, etc.
    STAR = 1
    # (One or more of previous construct) -> ab+c: abc, abbc, abbbc, etc.
    PLUS = 2
    # (Zero or one of previous construct) -> colou?r matches both "color" and "colour".
    QUESTION = 3

    # Range quantifiers
    # {n}: Matches the preceding token(s) exactly `n` times
    # {n,}: Matches the preceding token(s) `n` or more times
    # {m,n}: Matches the preceding token(s) between minimum `m` and maximum `n` times
    LBRACE = 4
    RBRACE = 5
    COMMA = 6

    # Alternative matches -> http|https matches one of: "http" or "https"
    PIPE = 7

    # Grouping
    # 1. Quantifier -> (ha)+ matches "ha", "haha", "hahaha", etc
    # 2. Capture grouping -> To capture the matched text: (\d{2}) - (\d{4}) matches "09-1996" and
    # captures the groups "09" and "1996"
    LPAREN = 8
    RPAREN = 9

    # Character classes
    # Matches any single character that is present inside the brackets.
    # m[ei]hai matches both "mehai" or "mihai". Some special cases are [a-z] which matches all
    # lowercase letter in the latin alphabet. Similar [A-Z] matches the uppercase and [0-9] matches
    # any digit
    LBRACKET = 10
    RBRACKET = 11

    # When used in a character class in the beginning: [^...], it matches all the characters which
    # are not in the class.
    # Example: [^aeiou] matches anything that is not a lowercase vowel
    CARRET = 12

    # When used in a character class between two characters, it defines a range
    # Example: [a-z] matches any lowercase letter. [a-zA-Z0-9] matches any alphanumerical character
    DASH = 13

    # Special characters
    # The "wildcard" matches any single character except a newline character.
    # Example: h.t matches "hat", "hot", "h1t", etc
    DOT = 14

    # An anchor. It asserts that the current position is the end of the string or the end of a line
    # in multiline mode.
    # Example: world$ match "hello world" but does not match "world peace".
    DOLLAR = 15

    # The escape character has 2 purposes:
    # 1. It removes the special meaning of a regex character: \. (to match a literal dot)
    # 2. It signals the start of a special sequence: \d, \w, \s
    BACKSLASH = 16

    # Special escape sequences
    DIGIT = 17  # \d - Matches any digit == [0-9]
    NON_DIGIT = 18  # \D - Matches any non-digit == [^0-9]
    WORD = 19  # \w - Matches any word character (alphanumeric and underscore) == [a-zA-Z0-9_]
    NON_WORD = 20  # \W - Matches any non-word character (alphanumeric and underscore) == [^a-zA-Z0-9_]
    WHITESPACE = 21  # \s - Matches any whitespace character == [ \t\n\r\f\v].
    NON_WHITESPACE = 21  # \S - Matches any non-whitespace character == [^ \t\n\r\f\v].

    # Word boundary - Matches the position between a word character (\w) and a non-word character
    # (\W) or the start/end of a string.
    # Example: \bcat\b matches "cat" in "The cat sat" but does not match "cat" in "tomcat".
    WORD_BOUNDARY = 22  # \b
    NON_WORD_BOUNDARY = 23  # \B

    # Backreferences
    # Matches the exact text that was previously captured by a capturing group ((...)). \1 refers to
    # the first group, \2 to the second group, etc.
    # Example: (\w)\1 matches any repeated character, like "oo" in "look" or "ll" in "hello"
    BACKREF = 24  # \1, \2, etc.

    # Lookahead / Lookbehind markers -> Like peek for regex
    # Example: (?= -> Password(?=.*[0-9]) checks if the password contains at least one digit.
    # "Password123" and "Password abc 123" will match.
    LOOKAHEAD_POS = 25  # (?=
    # Example: (?= -> Password(?!.*[0-9]) checks if the password does not contain any digit.
    # "Password123" and "Password abc 123" will not match.
    LOOKAHEAD_NEG = 26  # (?!
    # Example (?<=abc) checks if the string contains "abc" before the current position.
    LOOKBEHIND_POS = 27  # (?<=
    # Example (?<!abc) checks if the string does not contain "abc" before the current position.
    LOOKBEHIND_NEG = 28  # (?<!
    # Example (?:http|https):// groups "http" and "https" for the | operatior, but you can't
    # reference it as a captured group with \1
    NON_CAPTURING = 29  # (?:

    EOF = 30


@dataclass
class Token:
    t_type: TokenType
    value: Optional[str] = None
    position: int = 0


class Lexer:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.pos = 0  # Current index in the pattern
        self.length = len(pattern)

    def tokenize(self) -> list[Token]:
        """Convert the pattern into a stream of tokens"""
        tokens = []

        # While the cursor is not at the end of the string
        while self.pos < self.length:
            start_pos = self.pos
            curr_char = self.current_char()

            if curr_char == "\\":
                token = self._handle_escape()
                if token:
                    tokens.append(token)
            else:
                self.advance()

        return tokens

    def current_char(self) -> Optional[str]:
        """Get the character at the current position from the underlying lexer's pattern. This is
        essentially peek.
        """
        if self.pos >= self.length:
            return None
        else:
            return self.pattern[self.pos]

    def advance(self) -> Optional[str]:
        """Return the character at the current position and got to the next position"""
        char = self.current_char()
        self.pos += 1
        return char

    def _handle_escape(self) -> Optional[Token]:
        start_pos = self.pos
        _escape = self.advance()

        next_char = self.current_char()
        if next_char is None:
            raise ValueError(
                f"Pattern cannot end with backslash at position {self.pos}"
            )

        if next_char == "d":
            self.advance()
            return Token(TokenType.DIGIT, r"\d", start_pos)
        elif next_char == "D":
            self.advance()
            return Token(TokenType.NON_DIGIT, r"\D", start_pos)
        elif next_char == "w":
            self.advance()
            return Token(TokenType.WORD, r"\w", start_pos)
        elif next_char == "W":
            self.advance()
            return Token(TokenType.NON_WORD, r"\W", start_pos)
        elif next_char == "s":
            self.advance()
            return Token(TokenType.WHITESPACE, r"\s", start_pos)
        elif next_char == "S":
            self.advance()
            return Token(TokenType.NON_WHITESPACE, r"\S", start_pos)
        elif next_char == "b":
            self.advance()
            return Token(TokenType.WORD_BOUNDARY, r"\b", start_pos)
        elif next_char == "B":
            self.advance()
            return Token(TokenType.NON_WORD_BOUNDARY, r"\B", start_pos)
        elif next_char.isdigit():
            num = ""
            while next_char and next_char.isdigit():
                num += next_char
                self.advance()
                next_char = self.current_char()
            return Token(TokenType.BACKREF, f"\\{num}", start_pos)
        elif next_char == "\n":
            self.advance()
            return Token(TokenType.CHAR, "\n", start_pos)
        elif next_char == "\t":
            self.advance()
            return Token(TokenType.CHAR, "\t", start_pos)
        elif next_char == "\r":
            self.advance()
            return Token(TokenType.CHAR, "\r", start_pos)
        elif next_char == "\v":
            self.advance()
            return Token(TokenType.CHAR, "\v", start_pos)
        elif next_char == "\f":
            self.advance()
            return Token(TokenType.CHAR, "\f", start_pos)
        else:
            self.advance()
            return Token(TokenType.CHAR, next_char, start_pos)
