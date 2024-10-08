from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple

class Token(Enum):
    IDENTIFIER = 1
    OPERATOR = 2
    KEYWORD = 3
    LITERAL = 4
    PUNCTUATOR = 5
    NEWLINE = 6

@dataclass
class Lexeme:
    lexeme: str = field(default="")
    token: Token = field(default=None)

keywords = []

lexemes: List[Lexeme] = []
file_path = 'source.skibidi'

def get_lexeme(code: str, start: int) -> Tuple[Lexeme, int]:
    if code[start].isalpha():
        end = start + 1
        for end, char in enumerate(code[start+1:]):
            if not char.isidentifier():
                break
        lex = Lexeme(code[start:end], Token.IDENTIFIER)
        if lex.lexeme in keywords:
            lex.token = Token.KEYWORD
        return lex, end
    elif code[start].isnumeric() or code[start] == '+' or code[start] == '-':
        end = start + 1
        for end, char in enumerate(code[start+1:]):
            if not char.isnumeric():
                break
        lex = Lexeme(code[start:end], Token.LITERAL)
        return lex, end
    

with open(file_path, 'r') as file:
    code = file.read()

    i = 0
