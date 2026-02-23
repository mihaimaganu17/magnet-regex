from dataclasses import dataclass
from typing import Optional
from magnet_regex.ast_node import ASTNode, CharClassNode, CharNode, DotNode


@dataclass
class Match:
    """Represents a match over the text"""
    start: int
    end: int
    text: str
    # Contains the groups, mapping the group number to the captured text
    groups: dict[int, Optional[int]]

    def group(self, n: int = 0) -> Optional[str]:
        """Retrieves the group based on its index"""
        # If index is zero (\0), we return the entire match
        if n == 0:
            return self.text
        return self.group.get(n)


class Matcher:
    def __init__(self, ast: ASTNode, flags: Optional[dict[str, bool]] = None):
        self.ast = ast
        self.flags = flags or {}

        # Flags
        self.ignore_case = self.flags.get("ignorecase", False)
        self.multiline = self.flags.get("multiline", False)
        self.dotall = self.flags.get("dotall", False)

        # State during matching
        self.text = ""
        self.length = 0
        self.captures: dict[int, Optional[str]] = {}

    def match(self, text: str, start: int = 0) -> Optional[Match]:
        # Resetting previous state
        self.text = text
        self.length = len(text)
        self.captures = {}

        self._match_node(self.ast, start)

    def _match_node(self, node: ASTNode, pos: int) -> Optional[int]:
        """Dispatches the call to the appropriate handler based on node type and return the first
        integer offset after the match, if the node matches"""
        if pos >= self.length:
            return None

        if isinstance(node, CharNode):
            return self._match_char(node, pos)
        elif isinstance(node, DotNode):
            return self._match_dot(node, pos)
        elif isinstance(node, CharClassNode):
            return self._match_char_class(node, pos)


    def _match_char(self, node: CharNode, pos: int) -> Optional[int]:
        if pos >= self.length:
            return None

        text_char = self.text[pos]
        pattern_char = node.char

        if self.ignore_case:
            text_char = text_char.lower()
            pattern_char = pattern_char.lower()

        if text_char == pattern_char:
            return pos + 1

        return None

    def _match_dot(self, node: DotNode, pos: int) -> Optional[int]:
        """Dot matches any character, except newline. It also matches newline when the dotall
        option is enabled."""
        if pos >= self.length:
            return None

        char = self.text[pos]

        if not self.dotall and char == '\n':
            return None
        return pos + 1

    def _match_char_class(self, node: CharClassNode, pos: int) -> Optional[int]:
        if pos >= self.length:
            return None

        char = self.text[pos]
        chars = node.chars
        if self.ignore_case:
            char = char.lower()
            chars = set(char.lower for char in chars)

        char_belongs = char in chars

        if self.ignore_case:
            char = char.lower()

        if node.negated != char_belongs:
            return pos + 1
        else:
            return None