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

keywords = ['if', 'while', 'for']

lexemes: List[Lexeme] = []
file_path = 'source.skibidi'

def get_lexeme(code: str, start: int) -> Tuple[Lexeme, int]:
    if code[start].isalpha():
        end = start + 1
        for end, char in enumerate(code, start=start+1):
            if not char.isidentifier():
                break
        lex = Lexeme(code[start:end], Token.IDENTIFIER)
        if lex.lexeme in keywords:
            lex.token = Token.KEYWORD
        return lex, end
    elif code[start].isnumeric() or code[start] == '+' or code[start] == '-':
        end = start + 1
        for end, char in enumerate(code, start=start+1):
            if not char.isnumeric():
                break
        lex = Lexeme(code[start:end], Token.LITERAL)
        return lex, end
    elif code[start] == '\n':
        return Lexeme('\n', Token.NEWLINE), start + 1
    return Lexeme(), start + 1
    

with open(file_path, 'r') as file:
    code = file.read()

    for i, char in enumerate(code):
        print(f'{i}: {repr(char)}', end='', sep=', ')

    i = 0
    stop = 0
    while i < len(code) and stop < 10:
        if code[i] == ' ':
            i += 1
            continue
        print(f'start: {i}')
        lex, i = get_lexeme(code, i) 
        print(f'end: {i}')
        lexemes.append(lex)

        stop += 1
    print(lexemes)