from typing import List, Tuple, Dict
from lexical import Lexeme, Token
from varmap import VarMap

keywords = ['true', 'false', 'if', 'while', 'for', 'var', 'and', 'or', 'end', 'print']
symbols = ['+', '-', '*', '/', '%', '!', '=', '<', '>', '==', '!=', '<=', '>=']
punctuators = ['(', ')', '\"', ';']

# varmap: Dict[str, any] = {}
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
    elif code[start].isnumeric() or ((code[start] == '+' or code[start] == '-') and code[start+1].isnumeric()):
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
        case 'and' | 'or':
            return Lexeme(lex, Token.OPERATOR)
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
    varmap = VarMap()
    while i < len(lexemes):
        i = parse_statement(lexemes, i, varmap)
    
    print(varmap)

def parse_statement(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    lex = lexemes[start]
    match lex.token:
            case Token.KEYWORD if lex.lexeme == 'var':
                return parse_declare(lexemes, start, varmap)
            case Token.KEYWORD if lex.lexeme == 'print':
                return parse_print(lexemes, start, varmap)
            case Token.KEYWORD if lex.lexeme == 'if':
                return parse_if(lexemes, start, varmap)
            case Token.KEYWORD if lex.lexeme == 'while':
                return parse_while(lexemes, start, varmap)
            case Token.KEYWORD if lex.lexeme == 'for':
                return parse_for(lexemes, start, varmap)
            case Token.IDENTIFIER:
                return parse_assign(lexemes, start, varmap)
            case Token.NEWLINE:
                return start + 1
            case Token.KEYWORD if lex.lexeme == 'end':
                return start + 1
            case _:
                raise RuntimeError()

def parse_declare(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    identifier = lexemes[start+1]
    if identifier.token is not Token.IDENTIFIER:
        pass #TODO ERROR: invalid identifier
    elif identifier.lexeme in varmap:
        pass #TODO ERROR: identifier already taken
    operator = lexemes[start+2]
    if operator.lexeme != '=':
        pass #TODO ERROR: expected "=" symbol for assignment
    expression_parts: List[Lexeme] = build_expression(lexemes, start+3)
    expression = parse_expression(expression_parts, varmap)
    varmap.create_var(identifier.lexeme, expression)
    return start + 3 + len(expression_parts)

def parse_assign(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    var = lexemes[start]
    if var.lexeme not in varmap:
        pass #TODO: ERROR identifier not found
    operator = lexemes[start+1]
    if operator.lexeme != '=':
        pass #TODO ERROR
    expression_parts: List[Lexeme] = build_expression(lexemes, start+2)
    expression = parse_expression(expression_parts, varmap)
    varmap[var.lexeme] = expression
    return start + 2 + len(expression_parts)

def parse_print(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    left_parenthesis = lexemes[start+1]
    if left_parenthesis.lexeme != '(':
        pass #TODO: ERROR
    expression_parts = build_expression(lexemes, start+2)
    expression = parse_expression(expression_parts, varmap)
    print(expression)
    return start + 3 + len(expression_parts)

def parse_if(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    left_parenthesis = lexemes[start+1]
    expression_parts = build_expression(lexemes, start+2)
    right_parenthesis = lexemes[start+2+len(expression_parts)]

    expression = parse_expression(expression_parts, varmap)
    if expression is True:
        return start + 3 + len(expression_parts)
    elif expression is False:
        end_index = find_end(lexemes, start+3+len(expression_parts))
        return end_index + 1
    else:
        pass #TODO ERROR

def parse_while(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    left_parenthesis = lexemes[start+1]
    expression_parts = build_expression(lexemes, start+2)
    right_parenthesis = lexemes[start+2+len(expression_parts)]
    body_index = start + 3 + len(expression_parts)

    end_index = find_end(lexemes, body_index)
    expression = parse_expression(expression_parts, varmap)
    while expression is True:
        i = body_index
        varmap.open_scope()
        while i < end_index:
            i = parse_statement(lexemes, i, varmap)
        varmap.close_scope()
        expression = parse_expression(expression_parts, varmap)
    
    return end_index + 1

def parse_for(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    varmap.open_scope() # dumb solution, but this is so the variable declared in for loop gets deleted

    left_parenthesis = lexemes[start+1]
    semicolon1_index = parse_statement(lexemes, start + 2, varmap) # declare variable
    expression_parts = build_expression(lexemes, semicolon1_index + 1)
    semicolon2_index = len(expression_parts) + semicolon1_index + 1
    statement_index = semicolon2_index + 1
    body_index = statement_index + 1 + len(build_expression(lexemes, statement_index))
    # uses build_expression() to find ')'

    end_index = find_end(lexemes, body_index)
    expression = parse_expression(expression_parts, varmap)
    while expression is True:
        i = body_index
        varmap.open_scope()
        while i < end_index:
            i = parse_statement(lexemes, i, varmap)
        varmap.close_scope()
        parse_statement(lexemes, statement_index, varmap)
        expression = parse_expression(expression_parts, varmap)

    varmap.close_scope()
    return end_index + 1

# finds the index of the corresponding "end" keyword. used for if statements and loops
def find_end(lexemes: List[Lexeme], start: int) -> int:
    open_keywords = ['if', 'while', 'for']
    opened = 0
    index = start
    for lex in lexemes[start:]:
        if lex.lexeme in open_keywords:
            opened += 1
        if lex.lexeme == 'end' and opened <= 0:
            return index
        if lex.lexeme == 'end' and opened > 0:
            opened -= 1
        index += 1
    
def build_expression(lexemes: List[Lexeme], start: int) -> List[Lexeme]:
    expression = []
    parentheses = 0
    for lex in lexemes[start:]:
        if lex.token == Token.NEWLINE or lex.lexeme == ';':
            return expression
        elif lex.lexeme == ')' and parentheses <= 0:
            return expression
        elif lex.lexeme == ')' and parentheses > 0:
            parentheses -= 1
        elif lex.lexeme == '(':
            parentheses += 1
        expression.append(lex)
    return expression

# https://en.wikipedia.org/wiki/Shunting_yard_algorithm
# SHOUTOUT TO DIJKSTRA THE GOAT
def parse_expression(parts: List[Lexeme], varmap: VarMap):
    output_stack: List[Lexeme] = []
    operator_stack: List[Lexeme] = []

    for lex in parts:
        if lex.token is Token.LITERAL:
            output_stack.append(lex.lexeme)
        elif lex.token is Token.IDENTIFIER:
            # assert that [identifier] is in varmap
            output_stack.append(varmap[lex.lexeme])
        elif lex.token is Token.OPERATOR:
            while operator_stack and operator_stack[-1] != '(' and Lexeme.has_lower_precedence(lex.lexeme, operator_stack[-1]):
                
                # output_stack.append(operator_stack.pop())
                result = parse_operation(output_stack, operator_stack.pop())
                output_stack.append(result)
            operator_stack.append(lex.lexeme)
        elif lex.lexeme == '(':
            operator_stack.append(lex.lexeme)
        elif lex.lexeme == ')':
            while operator_stack[-1] != '(':
                # output_stack.append(operator_stack.pop())
                result = parse_operation(output_stack, operator_stack.pop())
                output_stack.append(result)
            #assert there is a left parenthesis at the top of the operator stack
            operator_stack.pop()
    for operator in operator_stack[::-1]:
        result = parse_operation(output_stack, operator)
        output_stack.append(result)
    return output_stack[0]

def parse_operation(output_stack: List[Lexeme], operator: str):
    operations = {
        '+': lambda t1, t2: t1 + t2,
        '-': lambda t1, t2: t1 - t2,
        '*': lambda t1, t2: t1 * t2,
        '/': lambda t1, t2: t1 / t2,
        '%': lambda t1, t2: t1 % t2,
        '==': lambda t1, t2: t1 == t2,
        '<': lambda t1, t2: t1 < t2,
        '>': lambda t1, t2: t1 > t2,
        '<=': lambda t1, t2: t1 <= t2,
        '>=': lambda t1, t2: t1 >= t2,
        '!=': lambda t1, t2: t1 != t2,
        'and': lambda t1, t2: t1 and t2,
        'or': lambda t1, t2: t1 or t2
    }

    if operator == '!':
        return not output_stack.pop()
    else:
        term2 = output_stack.pop()
        term1 = output_stack.pop()
        return operations[operator](term1, term2)

def main():
    with open(file_path, 'r') as file:
        code = file.read()

        # for i, char in enumerate(code):
        #     print(f'[{i}: {repr(char)}]')

        lexemes: List[Lexeme] = code_to_lexemes(code)
        print('--parsing--')
        parse_program(lexemes)
        print('--done parsing--')

if __name__ == '__main__':
    main()