from dataclasses import dataclass
from typing import Optional, Set


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


@dataclass
class QuantifierNode(ASTNode):
    """Quantifies a given node. Quantifiers can be: *, +, ?, {n}, {n,m}, {n,}. See lexer.py for
    more information"""
    child: ASTNode 
    min_count: int
    max_count: Optional[int]
    # Greedy mode (by default), matches as many characters as possible. For example, by default
    # the regex -> ".*" matches everything between 2 quotes, as such, for the string ->
    # "hello" some room "world" will be matched from the first quote (position 0) up to the last
    # quote (after world).
    # The lazy match will have 2 matches, one for each group of characters between quotes.
    # False for lazy qunatifiers: (*?, +?, ??, {n,m}?)
    greedy: bool = True

    def __repr__(self):
        q = None
        if self.min_count == 0 and self.max_count == 1:
            q = "?"
        elif self.min_count == 0 and self.max_count is None:
            q = "*"
        elif self.min_count == 1 and self.max_count is None:
            q = "+"
        else:
            q = f"{{{self.min_count}, {self.max_count}}}"
        
        if not self.greedy:
            q += "?"
        
        return f"Quantifier({self.child} {q})"