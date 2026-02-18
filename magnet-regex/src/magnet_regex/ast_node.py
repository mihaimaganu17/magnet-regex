from dataclasses import dataclass


@dataclass
class ASTNode:
    pass

@dataclass
class CharNode(ASTNode):
    char: str

    def __repr__(self):
        return f"Char({self.char!r})"