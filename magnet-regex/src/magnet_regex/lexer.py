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
    DIGIT = 17 # \d - Matches any digit == [0-9]
    NON_DIGIT = 18 # \D - Matches any non-digit == [^0-9]
    WORD = 19 # \w - Matches any word character (alphanumeric and underscore) == [a-zA-Z0-9_]
    NON_WORD = 20 # \W - Matches any non-word character (alphanumeric and underscore) == [^a-zA-Z0-9_]
    WHITESPACE = 21 # \s - Matches any whitespace character == [ \t\n\r\f\v].
    NON_WHITESPACE = 21 # \S - Matches any non-whitespace character == [^ \t\n\r\f\v].

    # Word boundary - Matches the position between a word character (\w) and a non-word character
    # (\W) or the start/end of a string.
    # Example: \bcat\b matches "cat" in "The cat sat" but does not match "cat" in "tomcat".
    WORD_BOUNDARY = 22 # \b
    NON_WORD_BOUNDARY = 23 # \B

    # Backreferences
    # Matches the exact text that was previously captured by a capturing group ((...)). \1 refers to
    # the first group, \2 to the second group, etc.
    # Example: (\w)\1 matches any repeated character, like "oo" in "look" or "ll" in "hello"
    BACKREF = 24 # \1, \2, etc.

@dataclass
class Token:
    t_type: TokenType
    value: Optional[str] = None
    position: int = 0