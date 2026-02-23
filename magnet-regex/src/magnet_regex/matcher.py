from dataclasses import dataclass
import string
from typing import Optional
from magnet_regex.ast_node import ASTNode, AlternationNonde, CharClassNode, CharNode, ConcatNode, DotNode, GroupNode, NonCapturingGroupNode, PredefinedClassNode, QuantifierNode


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
        elif isinstance(node, QuantifierNode):
            return self._match_quantifier(node, pos)
        elif isinstance(node, ConcatNode):
            return self._match_concat(node, pos)
        elif isinstance(node, AlternationNonde):
            return self._match_alternation(node, pos)
        elif isinstance(node, GroupNode):
            return self._match_group(node, pos)
        elif isinstance(node, NonCapturingGroupNode):
            return self._match_non_capturing_group(node, pos)

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

    def _match_quantifier(self, node: QuantifierNode, pos: int) -> Optional[int]:
        # Holds the first index offset after each match of the child node. It will be further filtered
        matches = []
        # Cursor to move along the text to collect all possible matches
        current_pos = pos
        count = 0

        while True:
            # If we reach or exceeded the max count, break out of the loop
            if node.max_count and count >= node.max_count:
                break

            next_pos = self._match_node(node.child, current_pos)

            if next_pos is None or next_pos == current_pos:
                break
            count += 1

            current_pos = next_pos
            matches.append(current_pos)

        # If we have a star quantifier, a minimum of 0 is also a valid match
        valid_matches = [pos] if node.min_count == 0 else []
        valid_matches.extend(
            # Only consider matches that fulfill minimum count
            [m for i, m in enumerate(matches, 1) if i >= node.min_count]
        )

        if not valid_matches:
            return None

        if node.greedy:
            return valid_matches[-1]
        else:
            return valid_matches[0]

    def _match_concat(self, node: ConcatNode, pos: int) -> Optional[int]:
        if not node.children:
            return pos

        return self._match_concat_recursive(node.children, 0, pos)

    def _match_concat_recursive(
        self, children: list[ASTNode], child_idx: int, pos: int
    ) -> Optional[int]:
        """Match the text starting at position `pos` recursively against the `children` nodes"""
        # If we matched up to `child_idx` and it it greater than the children node count, we have
        # a concat match and we return
        if child_idx >= len(children):
            return pos

        child = children[child_idx]

        if isinstance(child, QuantifierNode):
            # Holds the first index offset after each match of the child node. It will be further filtered
            matches = []
            # Cursor to move along the text to collect all possible matches
            current_pos = pos
            count = 0

            while True:
                # If we reach or exceeded the max count, break out of the loop
                if child.max_count and count >= child.max_count:
                    break

                next_pos = self._match_node(child.child, current_pos)

                if next_pos is None or next_pos == current_pos:
                    break
                count += 1

                current_pos = next_pos
                matches.append(current_pos)

            # If we have a star quantifier, a minimum of 0 is also a valid match
            valid_matches = [pos] if child.min_count == 0 else []
            valid_matches.extend(
                # Only consider matches that fulfill minimum count
                [m for i, m in enumerate(matches, 1) if i >= child.min_count]
            )

            if not valid_matches:
                return None

            # Refactor with match_quantifier until this point
            if child.greedy:
                valid_matches.reverse()

            # Try all the possible matches for the quantifier
            for match_end in valid_matches:
                # move forward in the children's list
                result_idx = self._match_concat_recursive(
                    children, child_idx + 1, match_end
                )
                if result_idx is not None:
                    return result_idx

            return None
        else:
            next_pos = self._match_node(child, pos)
            if next_pos is None:
                return None
            # If we reached this point, we matched and we go to the next child
            return self._match_concat_recursive(children, child_idx + 1, next_pos)

    def _match_alternation(self, node: AlternationNonde, pos: int) -> Optional[int]:
        for alt in node.alternatives:
            end_pos = self._match_node(alt, pos)

            if end_pos is not None:
                return end_pos
        return None

    def _match_group(self, node: GroupNode, pos: int) -> Optional[int]:
        # Save the old capture in case we need to backtrack
        old_capture = self.captures.get(node.group_number)

        end_pos = self._match_node(node.child, pos)

        # If we matched, we store the capture
        if end_pos is not None:
            self.captures[node.group_number] = self.text[pos:end_pos]
            return end_pos
        # TODO: Should this be in backreference?
        # else:
        #    if old_capture is not None:
        #        self.captures[node.group_number] = old_capture
        #    elif node.group_number in self.captures:
        #        del self.captures[node.group_number]
        return None

    def _match_non_capturing_group(self, node: NonCapturingGroupNode, pos: int) -> Optional[int]:
        end_pos = self._match_node(node.child, pos)

        return end_pos