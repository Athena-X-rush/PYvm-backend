from dataclasses import dataclass
from typing import List, Optional
import lexer

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class Assign(ASTNode):
    name: str
    value: ASTNode

@dataclass
class Print(ASTNode):
    args: List[ASTNode]

@dataclass
class Input(ASTNode):
    prompt: ASTNode

@dataclass
class If(ASTNode):
    condition: ASTNode
    body: List[ASTNode]
    elif_branches: List[tuple]  # list of (condition, body)
    else_body: Optional[List[ASTNode]]

@dataclass
class BinOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class Number(ASTNode):
    value: int

@dataclass
class String(ASTNode):
    value: str

@dataclass
class Identifier(ASTNode):
    name: str

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.current_token_value = self.lexer.current_token_value

    def parse(self):
        statements = []
        while self.current_token != 'EOF':
            if self.current_token == 'NEWLINE':
                self.current_token = self.lexer.get_next_token()
                self.current_token_value = self.lexer.current_token_value
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def statement(self):
        if self.current_token == 'PRINT':
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            if self.current_token != 'LPAREN':
                raise ValueError("Expected (")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            args = []
            if self.current_token != 'RPAREN':
                args.append(self.expression())
                while self.current_token == 'COMMA':
                    self.current_token = self.lexer.get_next_token()
                    self.current_token_value = self.lexer.current_token_value
                    args.append(self.expression())
            if self.current_token != 'RPAREN':
                raise ValueError("Expected )")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return Print(args)
        elif self.current_token == 'INPUT':
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            if self.current_token != 'LPAREN':
                raise ValueError("Expected (")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            prompt = self.expression() if self.current_token != 'RPAREN' else String('')
            if self.current_token != 'RPAREN':
                raise ValueError("Expected )")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return Input(prompt)
        elif self.current_token == 'IDENTIFIER':
            name = self.current_token_value
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            if self.current_token == 'ASSIGN':
                self.current_token = self.lexer.get_next_token()
                self.current_token_value = self.lexer.current_token_value
                value = self.expression()
                return Assign(name, value)
            elif self.current_token == 'LPAREN':
                self.current_token = self.lexer.get_next_token()
                self.current_token_value = self.lexer.current_token_value
                args = []
                if self.current_token != 'RPAREN':
                    args.append(self.expression())
                    while self.current_token == 'COMMA':
                        self.current_token = self.lexer.get_next_token()
                        self.current_token_value = self.lexer.current_token_value
                        args.append(self.expression())
                if self.current_token != 'RPAREN':
                    print(f"DEBUG: Expected RPAREN but got {self.current_token} with value {self.current_token_value}")
                    raise ValueError("Expected )")
                self.current_token = self.lexer.get_next_token()
                self.current_token_value = self.lexer.current_token_value
                if name == 'print':
                    return Print(args)
                elif name == 'input':
                    return Input(args[0] if args else String(''))
        elif self.current_token == 'IF':
            return self.if_statement()
        self.current_token = self.lexer.get_next_token()
        self.current_token_value = self.lexer.current_token_value
        return None

    def if_statement(self):
        self.current_token = self.lexer.get_next_token()  # skip IF
        self.current_token_value = self.lexer.current_token_value
        condition = self.expression()
        if self.current_token != 'COLON':
            raise ValueError("Expected :")
        self.current_token = self.lexer.get_next_token()
        self.current_token_value = self.lexer.current_token_value
        body = []
        while self.current_token not in ['ELIF', 'ELSE', 'EOF']:
            if self.current_token == 'NEWLINE':
                self.current_token = self.lexer.get_next_token()
                self.current_token_value = self.lexer.current_token_value
                continue
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        elif_branches = []
        while self.current_token == 'ELIF':
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            elif_condition = self.expression()
            if self.current_token != 'COLON':
                raise ValueError("Expected :")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            elif_body = []
            while self.current_token not in ['ELIF', 'ELSE', 'EOF']:
                if self.current_token == 'NEWLINE':
                    self.current_token = self.lexer.get_next_token()
                    self.current_token_value = self.lexer.current_token_value
                    continue
                stmt = self.statement()
                if stmt:
                    elif_body.append(stmt)
            elif_branches.append((elif_condition, elif_body))
        else_body = None
        if self.current_token == 'ELSE':
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            if self.current_token != 'COLON':
                raise ValueError("Expected :")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            else_body = []
            while self.current_token != 'EOF':
                if self.current_token == 'NEWLINE':
                    self.current_token = self.lexer.get_next_token()
                    self.current_token_value = self.lexer.current_token_value
                    continue
                stmt = self.statement()
                if stmt:
                    else_body.append(stmt)
        return If(condition, body, elif_branches, else_body)

    def expression(self):
        left = self.term()
        while self.current_token in ['PLUS', 'MINUS', 'EQUAL_EQUAL', 'LESS', 'GREATER']:
            op = self.current_token
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            right = self.term()
            left = BinOp(left, op, right)
        return left

    def term(self):
        left = self.factor()
        while self.current_token in ['MULTIPLY', 'DIVIDE']:
            op = self.current_token
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            right = self.factor()
            left = BinOp(left, op, right)
        return left

    def factor(self):
        if self.current_token == 'NUMBER':
            value = self.current_token_value
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return Number(value)
        elif self.current_token == 'STRING':
            value = self.current_token_value
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return String(value)
        elif self.current_token == 'IDENTIFIER':
            value = self.current_token_value
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return Identifier(value)
        elif self.current_token == 'INPUT':
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            if self.current_token != 'LPAREN':
                raise ValueError("Expected (")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            prompt = self.expression() if self.current_token != 'RPAREN' else String('')
            if self.current_token != 'RPAREN':
                raise ValueError("Expected )")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return Input(prompt)
        elif self.current_token == 'LPAREN':
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            expr = self.expression()
            if self.current_token != 'RPAREN':
                raise ValueError("Expected )")
            self.current_token = self.lexer.get_next_token()
            self.current_token_value = self.lexer.current_token_value
            return expr
        raise ValueError(f"Invalid token: {self.current_token}")
