from typing import List

file_path = 'source.skibidi'

var_map = {}
math_operators = ['+', '-', '/', '*', '%']


def process_code(code: List[str]):
    current_line = 0
    while current_line < len(code):
        line = code[current_line]
        line = line.strip()

        if line.startswith('var'):
            parse_declaration(line, current_line)
        elif line.startswith('print'):
            parse_print(line, current_line)
        elif line.startswith('if'):
            current_line = parse_if(line, current_line, code)

        current_line += 1

def parse_declaration(line: str, current_line: int):
    if '=' not in line:
        raise RuntimeError("variable declaration missing '=' symbol, line {}".format(current_line))
    line = line.replace(' ', '')[3:]
    line = line.split('=')
    if len(line) != 2:
        raise RuntimeError("invalid syntax for declaration, line {}".format(current_line))
    var = line[0]
    if var[0].isnumeric():
        raise RuntimeError("variable name cannot start with number, line {}".format(current_line))
    if var in var_map:
        raise RuntimeError("variable " + var + " is already defined, line {}".format(current_line))
    expression = parse_expression(line[1], current_line)
    var_map[var] = expression
    print(var_map)

def parse_expression(expression: str, current_line: int):
    if expression.isnumeric():
        return int(expression)
    elif expression == 'true':
        return True
    elif expression == 'false':
        return False
    elif expression.startswith('"') and expression.endswith('"'): #fix this later
        return expression[1:len(expression) - 1]
    else:
        if expression in var_map:
            return var_map[expression]
        else:
            #error for variable not found
            return 'VAR_NOT_FOUND'

def parse_print(expression: str, current_line: int):
    expression = expression[5:]
    if expression.startswith('(') and expression.endswith(')'):
        expression = expression[1:-1]
        print(parse_expression(expression, current_line))
    else:
        #error for invalid print function
        pass

def parse_if(expression: str, current_line: int, code: List[str]):
    #worry about nested later
    
    expression = expression[2:].strip()
    if parse_expression(expression, current_line) == True:
        return current_line
    
    end_line = current_line
    while end_line < len(code):
        if code[end_line].startswith('end'):
            break
        else:
            end_line += 1
    return end_line



def main():
    with open(file_path, 'r') as file:
        process_code(file.readlines())

if __name__ == "__main__":
    main()