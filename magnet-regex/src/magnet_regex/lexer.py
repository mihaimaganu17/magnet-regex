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

@dataclass
class Token:
    t_type: TokenType
    value: Optional[str] = None
    position: int = 0