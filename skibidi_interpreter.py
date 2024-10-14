import sys
from typing import List, Tuple
from lexical import Lexeme, Token
from varmap import VarMap

sys.tracebacklimit = 0 # this is to hide python's traceback on errors

keywords = ['true', 'false', 'if', 'elif', 'else', 'while', 'for', 'var', 'and', 'or', 'end', 'print']
symbols = ['+', '-', '*', '/', '%', '!', '=', '<', '>', '==', '!=', '<=', '>=']
punctuators = ['(', ')', '\"', '\'', ';']


def get_lexeme(code: str, start: int, line: int) -> Tuple[Lexeme, int]:
    if code[start].isalpha():
        end = start + 1
        for i in range(end, len(code)):
            char = code[i]
            if not (char.isalpha() or char.isnumeric() or char == '_'):
                end = i
                break
        else:
            # if the for loop terminates normally, we're at the end of the code
            end = len(code)
        lex = check_keyword(code[start:end])
        lex.line = line
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
        try:
            value = float(code[start:end])
        except ValueError:
            raise SyntaxError(f'Line {line}: invalid syntax for number') from None
        # "from None" hides the message "During handling of the above exception, another exception occurred"
        # probably a bad way to do it but i don't have time to look into it
        if value.is_integer():
            value = int(value)
        lex = Lexeme(value, Token.LITERAL, line)
        return lex, end
    elif code[start] == '\n':
        return Lexeme('\n', Token.NEWLINE, line), start + 1
    elif code[start] in symbols:
        end = start + 1
        if code[start:start+2] in ['==', '<=', '>=', '!=']:
            end = start + 2
        return Lexeme(code[start:end], Token.OPERATOR, line), end
    elif code[start] in punctuators and code[start] in ['\"', '\'']:
        open_char = code[start]
        end = start + 1
        found_close = False
        for i in range(end, len(code)):
            if code[i] == open_char:
                end = i
                found_close = True
                break
            elif code[i] == '\n':
                end = i
        if not found_close:
            raise SyntaxError(f'Line {line}: unclosed string literal')
        return Lexeme(code[start+1:end], Token.LITERAL, line), end + 1
    elif code[start] in punctuators:
        return Lexeme(code[start], Token.PUNCTUATOR, line), start + 1
    else:
        raise SyntaxError(f'Line {line}: invalid syntax')

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
    line = 1
    while i < len(code):
        if code[i] == ' ':
            i += 1
            continue
        lex, i = get_lexeme(code, i, line) 
        if lex.token is Token.NEWLINE:
            line += 1
        lexemes.append(lex)

    # [print(f'{i}: {lexeme}') for i, lexeme in enumerate(lexemes)]

    return lexemes

def parse_program(lexemes: List[Lexeme]):
    i = 0
    varmap = VarMap()
    while i < len(lexemes):
        i = parse_statement(lexemes, i, varmap)
    
    # print(varmap)

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
            case _:
                raise SyntaxError(f'Line {lex.line}: invalid syntax for statement')

def parse_declare(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    if start + 1 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected identifier')
    
    identifier = lexemes[start+1]
    if identifier.token is not Token.IDENTIFIER:
        raise SyntaxError(f'Line {lexemes[start].line}: expected identifier')
    elif identifier.lexeme in varmap:
        raise NameError(f'Line {lexemes[start].line}: identifier "{identifier.lexeme}" already taken')
    
    if start + 2 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected "=" for declaration')
    operator = lexemes[start+2]
    if operator.lexeme != '=':
        raise SyntaxError(f'Line {lexemes[start].line}: expected "=" for declaration')
    
    if start + 3 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected expression')
    expression_parts: List[Lexeme] = build_expression(lexemes, start+3)
    expression = parse_expression(expression_parts, varmap)
    varmap.create_var(identifier.lexeme, expression)
    return start + 3 + len(expression_parts)

def parse_assign(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    var = lexemes[start]
    if var.lexeme not in varmap:
        raise SyntaxError(f'Line {lexemes[start].line}: identifier "{var.lexeme}" not defined') # ERROR identifier not found
    
    if start + 1 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected "=" for assignment')
    operator = lexemes[start+1]
    if operator.lexeme != '=':
        raise SyntaxError(f'Line {lexemes[start].line}: expected "=" for assignment')
    
    if start + 2 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected expression')
    expression_parts: List[Lexeme] = build_expression(lexemes, start+2)
    expression = parse_expression(expression_parts, varmap)
    varmap[var.lexeme] = expression
    return start + 2 + len(expression_parts)

def parse_print(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    if start + 1 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected ( after print')
    left_parenthesis = lexemes[start+1]
    if left_parenthesis.lexeme != '(':
        raise SyntaxError(f'Line {lexemes[start].line}: expected ( after print')
    
    if start + 2 >= len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected expression')
    if lexemes[start+2].lexeme == ')':
        print()
        return start + 3
    expression_parts = build_expression(lexemes, start+2)
    expression = parse_expression(expression_parts, varmap)
    print(expression)
    return start + 3 + len(expression_parts)

def parse_if(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    keyword_index = start
    start_execution = start
    while lexemes[keyword_index].lexeme != 'end':
        match lexemes[keyword_index].lexeme:
            case 'if' | 'elif':
                if keyword_index + 1 >= len(lexemes):
                    raise SyntaxError(f'Line {lexemes[keyword_index].line}: expected (')
                left_parenthesis = lexemes[keyword_index+1]
                if left_parenthesis.lexeme != '(':
                    raise SyntaxError(f'Line {lexemes[keyword_index].line}: expected (')
                
                if keyword_index + 2 >= len(lexemes):
                    raise SyntaxError(f'Line {lexemes[keyword_index].line}: expected expression')
                expression_parts = build_expression(lexemes, keyword_index+2)

                if keyword_index + 2 + len(expression_parts) >= len(lexemes):
                    raise SyntaxError(f'Line {lexemes[keyword_index].line}: expected )')
                right_parenthesis = lexemes[keyword_index+2+len(expression_parts)]
                if right_parenthesis.lexeme != ')':
                    raise SyntaxError(f'Line {lexemes[keyword_index].line}: expected )')

                expression = parse_expression(expression_parts, varmap)
                if expression is True:
                    start_execution = keyword_index + 3 + len(expression_parts)
                    break
                elif expression is False:
                    keyword_index = find_end(lexemes, keyword_index + 3 + len(expression_parts), True)
                else:
                    raise TypeError(f'Line {lexemes[keyword_index].line}: expected boolean expression in "if" statement')
            case 'else':
                start_execution = keyword_index + 1
                break
    i = start_execution
    end_index = find_end(lexemes, i, True)
    varmap.open_scope()
    while i < end_index:
        i = parse_statement(lexemes, i, varmap)
    varmap.close_scope()
    if lexemes[end_index] == 'end':
        return end_index + 1
    else:
        return find_end(lexemes, end_index) + 1

def parse_while(lexemes: List[Lexeme], start: int, varmap: VarMap) -> int:
    if start + 1 > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected (')
    left_parenthesis = lexemes[start+1]
    if left_parenthesis.lexeme != '(':
        raise SyntaxError(f'Line {lexemes[start].line}: expected (')

    if start + 2 > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected expression')
    expression_parts = build_expression(lexemes, start+2)

    if start + start+2+len(expression_parts) > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected )')
    right_parenthesis = lexemes[start+2+len(expression_parts)]
    if right_parenthesis.lexeme != ')':
        raise SyntaxError(f'Line {lexemes[start].line}: expected )')

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

    if start + 1 > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected (')
    left_parenthesis = lexemes[start+1]
    if left_parenthesis.lexeme != '(':
        raise SyntaxError(f'Line {lexemes[start].line}: expected (')
    
    if start + 2 > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected ;')
    semicolon1_index = parse_statement(lexemes, start + 2, varmap) # declare variable
    if lexemes[semicolon1_index].lexeme != ';':
        raise SyntaxError(f'Line {lexemes[start].line}: expected ;')
    
    if semicolon1_index + 1 > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected expression')
    expression_parts = build_expression(lexemes, semicolon1_index + 1)

    if len(expression_parts) + semicolon1_index + 1 > len(lexemes):
        raise SyntaxError(f'Line {lexemes[start].line}: expected ;')
    semicolon2_index = len(expression_parts) + semicolon1_index + 1
    if lexemes[semicolon2_index].lexeme != ';':
        raise SyntaxError(f'Line {lexemes[start].line}: expected ;')

    statement_index = semicolon2_index + 1
    body_index = statement_index + 1 + len(build_expression(lexemes, statement_index))
    if body_index - 1 > len(lexemes) or lexemes[body_index - 1].lexeme != ')':
        raise SyntaxError(f'Line {lexemes[start].line}: expected )')
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
def find_end(lexemes: List[Lexeme], start: int, include_elif: bool = False) -> int:
    open_keywords = ['if', 'while', 'for']
    opened = 0
    index = start
    for lex in lexemes[start:]:
        if lex.lexeme in open_keywords:
            opened += 1
        elif lex.lexeme == 'end' and opened <= 0:
            return index
        elif include_elif and opened <= 0 and (lex.lexeme == 'elif' or lex.lexeme == 'else'):
            return index
        elif lex.lexeme == 'end' and opened > 0:
            opened -= 1
        index += 1
    raise SyntaxError(f'Line {lexemes[start].line}: expected "end"')
    
def build_expression(lexemes: List[Lexeme], start: int) -> List[Lexeme]:
    expression = []
    parentheses = 0
    for lex in lexemes[start:]:
        if lex.token is Token.KEYWORD:
            raise SyntaxError(f'Line {lexemes[start].line}: invalid expression')
        elif lex.token is Token.NEWLINE or lex.lexeme == ';':
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
            if lex.lexeme not in varmap:
                raise NameError(f'Line {lex.line}: identifier "{lex.lexeme}" not defined')
            output_stack.append(varmap[lex.lexeme])
        elif lex.token is Token.OPERATOR:
            while operator_stack and operator_stack[-1] != '(' and not Lexeme.has_higher_precedence(lex.lexeme, operator_stack[-1]):
                result = parse_operation(output_stack, operator_stack.pop())
                output_stack.append(result)
            operator_stack.append(lex.lexeme)
        elif lex.lexeme == '(':
            operator_stack.append(lex.lexeme)
        elif lex.lexeme == ')':
            while operator_stack[-1] != '(':
                result = parse_operation(output_stack, operator_stack.pop())
                output_stack.append(result)
            #assert there is a left parenthesis at the top of the operator stack
            operator_stack.pop()
    for operator in operator_stack[::-1]:
        if operator == '(':
            raise SyntaxError(f'Line {lex.line}: unclosed parentheses in expression')
        result = parse_operation(output_stack, operator)
        output_stack.append(result)
    if len(output_stack) != 1:
        raise SyntaxError(f'Line {lex.line}: invalid expression')
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
        if type(term1) is str or type(term2) is str:
            term1 = str(term1)
            term2 = str(term2)
        answer = operations[operator](term1, term2)
        if type(answer) is float and answer.is_integer():
            answer = int(answer)
        return answer

def main():
    if len(sys.argv) < 2:
        return
    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        code = file.read()

        lexemes: List[Lexeme] = code_to_lexemes(code)
        # print('--parsing--')
        parse_program(lexemes)
        # print('--done parsing--')

if __name__ == '__main__':
    main()