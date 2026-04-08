from parser import ASTNode, Program, Assign, Print, Input, If, BinOp, Number, String, Identifier

class Interpreter:
    def __init__(self, input_callback=None):
        self.variables = {}
        self.input_callback = input_callback
        self.output = []

    def execute(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                result = self.execute(stmt)
                if isinstance(result, dict) and result.get('needs_input'):
                    result['output'] = '\n'.join(self.output)
                    return result
            return '\n'.join(self.output)
        elif isinstance(node, Assign):
            value = self.evaluate(node.value)
            if isinstance(value, dict) and value.get('needs_input'):
                value['output'] = '\n'.join(self.output)
                return value
            self.variables[node.name] = value
        elif isinstance(node, Print):
            values = []
            for arg in node.args:
                val = self.evaluate(arg)
                if isinstance(val, dict) and val.get('needs_input'):
                    val['output'] = '\n'.join(self.output)
                    return val
                values.append(val)
            self.output.append(' '.join(str(v) for v in values))
        elif isinstance(node, Input):
            prompt = self.evaluate(node.prompt)
            if isinstance(prompt, dict) and prompt.get('needs_input'):
                prompt['output'] = '\n'.join(self.output)
                return prompt
            if self.input_callback:
                value = self.input_callback()
                if value is None:
                    return {'needs_input': True, 'input_prompt': str(prompt), 'output': '\n'.join(self.output)}
                return value
            else:
                return input(str(prompt))
        elif isinstance(node, If):
            condition = self.evaluate(node.condition)
            if isinstance(condition, dict) and condition.get('needs_input'):
                condition['output'] = '\n'.join(self.output)
                return condition
            if condition:
                for stmt in node.body:
                    result = self.execute(stmt)
                    if isinstance(result, dict) and result.get('needs_input'):
                        result['output'] = '\n'.join(self.output)
                        return result
            else:
                for cond, body in node.elif_branches:
                    elif_condition = self.evaluate(cond)
                    if isinstance(elif_condition, dict) and elif_condition.get('needs_input'):
                        elif_condition['output'] = '\n'.join(self.output)
                        return elif_condition
                    if elif_condition:
                        for stmt in body:
                            result = self.execute(stmt)
                            if isinstance(result, dict) and result.get('needs_input'):
                                result['output'] = '\n'.join(self.output)
                                return result
                        break
                else:
                    if node.else_body:
                        for stmt in node.else_body:
                            result = self.execute(stmt)
                            if isinstance(result, dict) and result.get('needs_input'):
                                result['output'] = '\n'.join(self.output)
                                return result

    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, String):
            return node.value
        elif isinstance(node, Identifier):
            return self.variables.get(node.name, 0)
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            if isinstance(left, dict) and left.get('needs_input'):
                return left
            right = self.evaluate(node.right)
            if isinstance(right, dict) and right.get('needs_input'):
                return right
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                return left / right
            elif node.op == '==':
                return left == right
            elif node.op == '<':
                return left < right
            elif node.op == '>':
                return left > right
        return 0
