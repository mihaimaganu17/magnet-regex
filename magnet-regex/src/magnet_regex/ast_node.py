from dataclasses import dataclass
from typing import Set


@dataclass
class ASTNode:
    pass

@dataclass
class CharNode(ASTNode):
    char: str

    def __repr__(self):
        return f"Char({self.char!r})"

@dataclass
class DotNode(ASTNode): 
    def __repr__(self):
        return "Dor(.)"

@dataclass
class CharClassNode(ASTNode): 
    """Characters with regex brackets `[...]`"""
    chars: Set[str]
    negated: bool = False # True if the class contains a caret: [^m]

    def __repr__(self):
        prefix = "^" if self.negated else ""
        chars_str = "".join(sorted(self.chars)[:10])
        if len(self.chars) > 10:
            chars_str += "..."
        return f"CharClass([{prefix}{chars_str}])"


@dataclass
class PredefinedClassNode(ASTNode):
    """A class node with a known key characteristic: \d, \D, \w, \W, etc"""
    # TODO: Shoud this be a enum?
    class_type: str

    def __repr__(self):
        return f"PredefinedClass(\\{self.class_type})"