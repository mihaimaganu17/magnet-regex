from dataclasses import dataclass
import string
from typing import Optional
from magnet_regex.ast_node import ASTNode, CharClassNode, CharNode, DotNode, PredefinedClassNode


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

        self._init_char_classes()

    def _init_char_classes(self):
        self.digit_chars = set("0123456789")
        lowercase_letters = [
            "".join([chr(l) for l in range(ord("a"), ord("z") + 1)])
        ]
        uppercase_letters = [
            "".join([chr(l) for l in range(ord("A"), ord("Z") + 1)])
        ]
        self.word_chars = set(lowercase_letters + uppercase_letters + self.digit_chars + "_")
        # OR
        self.word_chars = set(string.ascii_letters + string.digits + "_")
        self.whitespace_chars = set(" \t\n\r\f\v")

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
        elif isinstance(node, PredefinedClassNode):
            return self._match_predefined_class(node, pos)


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

    def _match_predefined_class(self, node: PredefinedClassNode, pos: int) -> Optional[int]:
        if pos >= self.length:
            return None

        char = self.text[pos]
        matched = False

        if node.class_type == 'd':
            matched = char in self.digit_chars
        elif node.class_type == "D":
            matched = char not in self.digit_chars
        elif node.class_type == 'w':
            matched = char in self.word_chars
        elif node.class_type == 'W':
            matched = char not in self.word_chars
        elif node.class_type == 's':
            matched = char in self.whitespace_chars
        elif node.class_type == 'S':
            matched = char not in self.whitespace_chars

        if matched:
            return pos + 1

        return None