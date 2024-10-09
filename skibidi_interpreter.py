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

    def __repr__(self) -> str:
        return f"('{self.token}': {repr(self.lexeme)})"


keywords = ['true', 'false', 'if', 'while', 'for', 'var', 'and', 'or', 'end', 'print']
symbols = ['+', '-', '*', '/', '%', '!', '=', '<', '>', '==', '!=', '<=', '>=']
punctuators = ['(', ')']

lexemes: List[Lexeme] = []
file_path = 'source.skibidi'

def get_lexeme(code: str, start: int) -> Tuple[Lexeme, int]:
    if code[start].isalpha():
        end = start + 1
        for i in range(end, len(code)):
            char = code[i]
            if not char.isidentifier():
                end = i
                break
        else:
            # if the for loop terminates normally, we're at the end of the code
            end = len(code)
        lex = Lexeme(code[start:end], Token.IDENTIFIER)
        token = check_token(lex.lexeme)
        if token is not None:
            lex.token = token
        return lex, end
    elif code[start].isnumeric() or code[start] == '+' or code[start] == '-':
        end = start + 1
        for i in range(end, len(code)):
            char = code[i]
            if not char.isnumeric():
                end = i
                break
        lex = Lexeme(code[start:end], Token.LITERAL)
        return lex, end
    elif code[start] == '\n':
        return Lexeme('\n', Token.NEWLINE), start + 1
    elif code[start] in symbols:
        end = start + 1
        if code[start:start+2] in ['==', '<=', '>=', '!=']:
            end = start + 2
        return Lexeme(code[start:end], Token.OPERATOR), end
    elif code[start] in punctuators:
        return Lexeme(code[start], Token.PUNCTUATOR), start + 1
    return Lexeme(), start + 1

def check_token(lexeme: str) -> Token:
    if lexeme not in keywords:
        return None
    if lexeme in ['true', 'false']:
        return Token.LITERAL
    else:
        return Token.KEYWORD

with open(file_path, 'r') as file:
    code = file.read()

    # for i, char in enumerate(code):
    #     print(f'[{i}: {repr(char)}]')

    i = 0
    while i < len(code):
        if code[i] == ' ':
            i += 1
            continue
        lex, i = get_lexeme(code, i) 
        lexemes.append(lex)
    
    [print(f'{i}: {lexeme}') for i, lexeme in enumerate(lexemes)]