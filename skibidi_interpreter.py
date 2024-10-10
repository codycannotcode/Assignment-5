from typing import List, Tuple, Dict
from lexical import Lexeme, Token

keywords = ['true', 'false', 'if', 'while', 'for', 'var', 'and', 'or', 'end', 'print']
symbols = ['+', '-', '*', '/', '%', '!', '=', '<', '>', '==', '!=', '<=', '>=']
punctuators = ['(', ')', '\"',]

varmap: Dict[str, any] = {}
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
        lex = check_keyword(code[start:end])
        return lex, end
    elif code[start].isnumeric() or code[start] == '+' or code[start] == '-':
        end = start + 1
        for i in range(end, len(code)):
            char = code[i]
            if not char.isnumeric() and char != '.':
                end = i
                break
        else:
            end = len(code)
        #TODO: catch error here if invalid number
        value = float(code[start:end])
        if value.is_integer():
            value = int(value)
        lex = Lexeme(value, Token.LITERAL)
        return lex, end
    elif code[start] == '\n':
        return Lexeme('\n', Token.NEWLINE), start + 1
    elif code[start] in symbols:
        end = start + 1
        if code[start:start+2] in ['==', '<=', '>=', '!=']:
            end = start + 2
        return Lexeme(code[start:end], Token.OPERATOR), end
    elif code[start] in punctuators and code[start] in ['\"', '\'']:
        open_char = code[start]
        end = start + 1
        for i in range(end, len(code)):
            if code[i] == open_char:
                end = i
                break
        else:
            pass #TODO ERROR for unclosed string
        return Lexeme(code[start+1:end], Token.LITERAL), end + 1
    elif code[start] in punctuators:
        return Lexeme(code[start], Token.PUNCTUATOR), start + 1
    return Lexeme(), start + 1

def check_keyword(lex: str) -> Lexeme:
    if lex not in keywords:
        return Lexeme(lex, Token.IDENTIFIER)
    match lex:
        case 'true':
            return Lexeme(True, Token.LITERAL)
        case 'false':
            return Lexeme(False, Token.LITERAL)
        case _:
            return Lexeme(lex, Token.KEYWORD)

def code_to_lexemes(code: str) -> List[Lexeme]:
    lexemes = []

    i = 0
    while i < len(code):
        if code[i] == ' ':
            i += 1
            continue
        lex, i = get_lexeme(code, i) 
        lexemes.append(lex)

    [print(f'{i}: {lexeme}') for i, lexeme in enumerate(lexemes)]

    return lexemes

def parse_program(lexemes: List[Lexeme]):
    i = 0
    while i < len(lexemes):
        lex = lexemes[i]
        match lex.token:
            case Token.KEYWORD if lex.lexeme == 'var':
                i = parse_declare(lexemes, i)
            case Token.KEYWORD if lex.lexeme == 'print':
                i = parse_print(lexemes, i)
            case Token.IDENTIFIER:
                i = parse_assign(lexemes, i)
            case Token.NEWLINE:
                i += 1
            case _:
                raise RuntimeError()

def parse_declare(lexemes: List[Lexeme], start: int) -> int:
    identifier = lexemes[start+1]
    if identifier.token is not Token.IDENTIFIER:
        pass #TODO ERROR: invalid identifier
    elif identifier.lexeme in varmap:
        pass #TODO ERROR: identifier already taken
    operator = lexemes[start+2]
    if operator.lexeme != '=':
        pass #TODO ERROR: expected "=" symbol for assignment
    expression_parts: List[Lexeme] = []
    for lex in lexemes[start+3:]:
        if is_line_end(lex):
            break
        expression_parts.append(lex)
    expression = parse_expression(expression_parts)
    varmap[identifier.lexeme] = expression
    return start + 3 + len(expression_parts)

def parse_assign(lexemes: List[Lexeme], start: int) -> int:
    var = lexemes[start]
    if var.lexeme not in varmap:
        pass #TODO: ERROR identifier not found
    operator = lexemes[start+1]
    if operator.lexeme != '=':
        pass #TODO ERROR
    expression_parts: List[Lexeme] = []
    for lex in lexemes[start+2:]:
        if is_line_end(lex):
            break
        expression_parts.append(lex)
    expression = parse_expression(expression_parts)
    varmap[var.lexeme] = expression
    return start + 2 + len(expression_parts)

def parse_print(lexemes: List[Lexeme], start: int) -> int:
    left_parenthesis = lexemes[start+1]
    if left_parenthesis.lexeme != '(':
        pass #TODO: ERROR
    expression_parts: List[Lexeme] = []
    for lex in lexemes[start+2:]:
        if lex.lexeme == ')':
            break
        expression_parts.append(lex)
    expression = parse_expression(expression_parts)
    print(expression)
    return start + 3 + len(expression_parts)

def parse_expression(parts: List[Lexeme]):
    if len(parts) == 1:
        lex = parts[0]
        if lex.token is Token.LITERAL:
            return lex.lexeme
        elif lex.token is Token.IDENTIFIER:
            if lex.lexeme in varmap:
                return varmap[lex.lexeme]
            else:
                pass #TODO: ERROR identifier not found
        else:
            pass #TODO: ERROR invalid expression

def is_line_end(lex: Lexeme):
    return lex.token is Token.NEWLINE

def main():
    with open(file_path, 'r') as file:
        code = file.read()

        # for i, char in enumerate(code):
        #     print(f'[{i}: {repr(char)}]')

        lexemes: List[Lexeme] = code_to_lexemes(code)
        print('--parsing--')
        parse_program(lexemes)
        print(varmap)
        print('--done parsing--')

if __name__ == '__main__':
    main()