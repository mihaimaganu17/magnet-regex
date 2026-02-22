from dataclasses import dataclass
from typing import Optional
from magnet_regex.ast_node import ASTNode


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