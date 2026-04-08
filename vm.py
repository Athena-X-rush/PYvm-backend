class BytecodeCompiler:
    def __init__(self):
        self.vars = set()  # Track variable names

    def compile(self, code):
        instructions = []
        lines = code.split('\n')
        label_id = 0

        def new_label():
            nonlocal label_id
            label_id += 1
            return f"L{label_id}"

        # First pass: collect variable assignments
        for line in lines:
            line = line.strip()
            if '=' in line and ':' not in line and not line.startswith('#'):
                var = line.split('=')[0].strip()
                self.vars.add(var)

        end_labels = []
        if_stack = []  # Track if-elif-else blocks

        for line_num, line in enumerate(lines):
            if not line.strip() or line.strip().startswith('#'):
                continue

            line = line.strip()

            # Handle if statements
            if line.startswith("if") and ":" in line:
                cond = line[2:line.rfind(":")].strip()
                end_label = new_label()
                else_label = new_label()
                instructions.append(("EVAL", cond, line_num + 1))
                instructions.append(("JUMP_IF_FALSE", else_label, line_num + 1))
                if_stack.append(('if', end_label, else_label))

            # Handle elif statements
            elif line.startswith("elif") and ":" in line and if_stack:
                cond = line[4:line.rfind(":")].strip()
                block_type, end_label, else_label = if_stack[-1]
                if block_type == 'if':
                    instructions.append(("JUMP", end_label, line_num + 1))
                    instructions.append(("LABEL", else_label, line_num + 1))
                    new_else = new_label()
                    instructions.append(("EVAL", cond, line_num + 1))
                    instructions.append(("JUMP_IF_FALSE", new_else, line_num + 1))
                    if_stack[-1] = ('elif', end_label, new_else)

            # Handle else statements
            elif line.startswith("else") and ":" in line and if_stack:
                block_type, end_label, else_label = if_stack[-1]
                if block_type in ['if', 'elif']:
                    instructions.append(("JUMP", end_label, line_num + 1))
                    instructions.append(("LABEL", else_label, line_num + 1))
                    if_stack[-1] = ('else', end_label, None)

            # Handle while loops
            elif line.startswith("while") and ":" in line:
                cond = line[5:line.rfind(":")].strip()
                start_label = new_label()
                end_label = new_label()
                instructions.append(("LABEL", start_label, line_num + 1))
                instructions.append(("EVAL", cond, line_num + 1))
                instructions.append(("JUMP_IF_FALSE", end_label, line_num + 1))
                if_stack.append(('while', start_label, end_label))

            # Handle assignments (including input assignments)
            elif "=" in line and not line.startswith(" ") and ":" not in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    var = parts[0].strip()
                    val = parts[1].strip()
                    # Check if it's an input assignment
                    if val.startswith('input(') and val.endswith(')'):
                        content = val[6:-1].strip()
                        if content.startswith('"') and content.endswith('"'):
                            content = content[1:-1]
                        elif content.startswith("'") and content.endswith("'"):
                            content = content[1:-1]
                        instructions.append(("INPUT", content, line_num + 1))
                        instructions.append(("STORE", var, line_num + 1))
                    else:
                        instructions.append(("PUSH", val, line_num + 1))
                        instructions.append(("STORE", var, line_num + 1))

            # Handle print statements
            elif line.startswith("print(") and line.endswith(")"):
                content = line[6:-1].strip()
                # Handle multiple arguments
                if "," in content:
                    args = [arg.strip() for arg in content.split(",")]
                    for arg in args:
                        if arg.startswith('"') and arg.endswith('"'):
                            arg = arg[1:-1]
                        elif arg.startswith("'") and arg.endswith("'"):
                            arg = arg[1:-1]
                        instructions.append(("PUSH", arg, line_num + 1))
                    instructions.append(("PRINT_MULTI", len(args), line_num + 1))
                else:
                    # Single argument
                    if content.startswith('"') and content.endswith('"'):
                        content = content[1:-1]
                    elif content.startswith("'") and content.endswith("'"):
                        content = content[1:-1]
                    instructions.append(("PUSH", content, line_num + 1))
                    instructions.append(("PRINT", None, line_num + 1))

        # Close remaining blocks
        while if_stack:
            block_type, label1, label2 = if_stack.pop()
            if block_type == 'while':
                instructions.append(("JUMP", label1, 0))  # JUMP doesn't need line number
                instructions.append(("LABEL", label2, 0))
            else:
                if label2:
                    instructions.append(("LABEL", label2, 0))
                instructions.append(("LABEL", label1, 0))

        return instructions


class VirtualMachine:
    def __init__(self, input_callback=None):
        self.stack = []
        self.vars = {}
        self.output = []
        self.trace = []
        self.input_callback = input_callback

    def eval_expr(self, expr):
        try:
            # Handle string literals
            if expr.startswith('"') and expr.endswith('"'):
                return expr[1:-1]
            elif expr.startswith("'") and expr.endswith("'"):
                return expr[1:-1]
            # Handle numbers
            elif expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                return int(expr)
            # Handle variables
            elif expr in self.vars:
                return self.vars[expr]
            # Handle simple expressions
            else:
                return eval(expr, {}, self.vars)
        except:
            return expr.strip('"\'')

    def run(self, instructions):
        labels = {}
        for i, instruction in enumerate(instructions):
            op = instruction[0]
            if op == "LABEL":
                labels[instruction[1]] = i

        i = 0
        while i < len(instructions):
            instruction = instructions[i]
            
            # Handle both old format (2-tuple) and new format (3-tuple with line number)
            if len(instruction) == 3:
                op, val, line_num = instruction
            else:
                op, val = instruction
                line_num = 0

            self.trace.append({
                "step": i,
                "op": op,
                "val": val,
                "line": line_num,  # Add line number to trace
                "stack": list(self.stack),
                "vars": dict(self.vars)
            })

            if op == "PUSH":
                self.stack.append(self.eval_expr(val))

            elif op == "STORE":
                if self.stack:
                    self.vars[val] = self.stack.pop()

            elif op == "PRINT":
                if self.stack:
                    value = self.stack.pop()
                    self.output.append(str(value))
                    
            elif op == "PRINT_MULTI":
                arg_count = val
                args = []
                for _ in range(arg_count):
                    if self.stack:
                        args.insert(0, str(self.stack.pop()))
                self.output.append(' '.join(args))
                
            elif op == "INPUT":
                # Handle input operation
                if self.input_callback:
                    user_input = self.input_callback(val)
                    self.stack.append(user_input)
                else:
                    # Default input for testing
                    self.stack.append("default_input")
                    self.output.append(f"[Input needed: {val}]")

            elif op == "EVAL":
                result = self.eval_expr(val)
                self.stack.append(bool(result))

            elif op == "JUMP_IF_FALSE":
                if self.stack and not self.stack.pop():
                    if val in labels:
                        i = labels[val]
                        continue

            elif op == "JUMP":
                if val in labels:
                    i = labels[val]
                    continue

            i += 1

        return "\n".join(self.output), self.trace
