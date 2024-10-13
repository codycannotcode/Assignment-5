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
    line: int = field(default=0)

    # returns True if operator1 has lower precedence than operator2
    @staticmethod
    def has_lower_precedence(operator1: str, operator2: str):
        # operators with a higher number have higher precedence
        precedence = {
            '*': 5,
            '/': 5,
            '%': 5,
            '+': 4,
            '-': 4,
            '<': 3,
            '<=': 3,
            '>': 3,
            '>=': 3,
            '!=': 3,
            '==': 3,
            '!': 2,
            'and': 1,
            'or': 0
        }
        return precedence[operator1] < precedence[operator2]

    def __repr__(self) -> str:
        return f"({self.token}: {repr(self.lexeme)}, line {self.line})"