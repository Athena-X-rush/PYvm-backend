from enum import Enum

class TokenType(Enum):
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    IF = 'IF'
    ELIF = 'ELIF'
    ELSE = 'ELSE'
    PRINT = 'PRINT'
    INPUT = 'INPUT'
    ASSIGN = 'ASSIGN'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    COLON = 'COLON'
    COMMA = 'COMMA'
    EQUAL_EQUAL = 'EQUAL_EQUAL'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    LESS = 'LESS'
    GREATER = 'GREATER'
    NEWLINE = 'NEWLINE'
    EOF = 'EOF'

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.current_char = self.code[0] if self.code else None
        self.current_token_value = None
        self.keywords = {
            'if': 'IF',
            'elif': 'ELIF',
            'else': 'ELSE',
            'print': 'PRINT',
            'input': 'INPUT'
        }

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.code):
            self.current_char = None
        else:
            self.current_char = self.code[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.code):
            return None
        return self.code[peek_pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace() and self.current_char != '\n':
            self.advance()

    def read_number(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def read_identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def read_string(self):
        self.advance()  # skip opening quote
        result = ''
        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance()  # skip closing quote
        return result

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                if self.current_char == '\n':
                    self.advance()
                    return 'NEWLINE'
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                self.current_token_value = self.read_number()
                return 'NUMBER'
            if self.current_char == '"':
                self.current_token_value = self.read_string()
                return 'STRING'
            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.read_identifier()
                self.current_token_value = identifier
                token_type = self.keywords.get(identifier, 'IDENTIFIER')
                return token_type
            if self.current_char == ':':
                self.advance()
                return 'COLON'
            if self.current_char == ',':
                self.advance()
                return 'COMMA'
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return 'EQUAL_EQUAL'
                self.advance()
                return 'ASSIGN'
            if self.current_char == '+':
                self.advance()
                return 'PLUS'
            if self.current_char == '-':
                self.advance()
                return 'MINUS'
            if self.current_char == '*':
                self.advance()
                return 'MULTIPLY'
            if self.current_char == '/':
                self.advance()
                return 'DIVIDE'
            if self.current_char == '<':
                self.advance()
                return 'LESS'
            if self.current_char == '>':
                self.advance()
                return 'GREATER'
            if self.current_char == '(':
                self.advance()
                return 'LPAREN'
            if self.current_char == ')':
                self.advance()
                return 'RPAREN'
            raise ValueError(f"Invalid character: {self.current_char}")
        return 'EOF'
