from dataclasses import dataclass, field
from enum import Enum

class Token(Enum):
    IDENTIFIER = 1
    OPERATOR = 2
    KEYWORD = 3
    LITERAL = 4
    PUNCTUATOR = 5
    NEWLINE = 6

@dataclass
class Lexeme:
    lexeme: str | int | bool | float = field(default=None)
    token: Token = field(default=None)

    def __repr__(self) -> str:
        return f"({self.token}: {repr(self.lexeme)})"