class BytecodeCompileError(Exception):
    def __init__(self, message, line_num=None, source_line=None):
        self.message = message
        self.line_num = line_num
        self.source_line = source_line
        super().__init__(self.__str__())

    def __str__(self):
        if self.line_num is None:
            return self.message
        if self.source_line:
            return f"Line {self.line_num}: {self.message}\n  -> {self.source_line}"
        return f"Line {self.line_num}: {self.message}"


class BytecodeRuntimeError(Exception):
    def __init__(self, message, line_num=None, op=None, operand=None):
        self.message = message
        self.line_num = line_num
        self.op = op
        self.operand = operand
        super().__init__(self.__str__())

    def __str__(self):
        parts = []
        if self.line_num:
            parts.append(f"Line {self.line_num}")
        if self.op:
            operand_text = "" if self.operand is None else f" {self.operand}"
            parts.append(f"during {self.op}{operand_text}")
        prefix = ": ".join(parts)
        return f"{prefix}: {self.message}" if prefix else self.message


class BytecodeCompiler:
    def __init__(self):
        self.vars = set()

    def compile(self, code):
        instructions = []
        lines = code.split("\n")
        label_id = 0
        unsupported_prefixes = {
            "import ": "Imports are not supported in this mini language.",
            "from ": "Imports are not supported in this mini language.",
            "def ": "Function definitions are not supported yet.",
            "for ": "For-loops are not supported yet. Use while instead.",
            "try:": "try/except is not supported yet.",
            "except ": "try/except is not supported yet.",
            "class ": "Classes are not supported yet.",
            "return": "return is not supported yet.",
            "break": "break is not supported yet.",
            "continue": "continue is not supported yet.",
        }

        def new_label():
            nonlocal label_id
            label_id += 1
            return f"L{label_id}"

        def compile_error(line_num, source_line, message):
            raise BytecodeCompileError(message, line_num, source_line.strip())

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if (
                "=" in stripped
                and ":" not in stripped
                and not stripped.startswith("#")
                and not stripped.startswith("print")
                and not stripped.startswith("if")
                and not stripped.startswith("elif")
                and not stripped.startswith("while")
            ):
                var_name = stripped.split("=", 1)[0].strip()
                if not var_name.isidentifier():
                    compile_error(line_num, line, f"Invalid assignment target '{var_name}'.")
                self.vars.add(var_name)

        control_flow_stack = []
        indent_stack = [0]

        for line_num, raw_line in enumerate(lines, start=1):
            stripped_line = raw_line.strip()
            if not stripped_line or stripped_line.startswith("#"):
                continue

            indent = len(raw_line) - len(raw_line.lstrip())
            line = stripped_line

            for prefix, message in unsupported_prefixes.items():
                if line.startswith(prefix):
                    compile_error(line_num, raw_line, message)

            is_chain_branch = line.startswith("elif ") or line.startswith("else")
            while control_flow_stack:
                block_type, end_label, else_label, start_label = control_flow_stack[-1]
                block_indent = indent_stack[-1]
                should_close = indent < block_indent or (
                    indent == block_indent
                    and not (is_chain_branch and block_type in ("if", "elif"))
                )
                if not should_close:
                    break

                control_flow_stack.pop()
                indent_stack.pop()

                if block_type == "while":
                    instructions.append(("JUMP", start_label, line_num))
                    instructions.append(("LABEL", end_label, line_num))
                elif block_type in ("if", "elif"):
                    if not is_chain_branch:
                        if else_label:
                            instructions.append(("LABEL", else_label, line_num))
                        instructions.append(("LABEL", end_label, line_num))
                elif block_type == "else":
                    instructions.append(("LABEL", end_label, line_num))

            if line.startswith("elif") and line.endswith(":") and control_flow_stack:
                condition = line[4:-1].strip()
                _, end_label, else_label, _ = control_flow_stack[-1]
                instructions.append(("JUMP", end_label, line_num))
                instructions.append(("LABEL", else_label, line_num))
                next_else_label = new_label()
                instructions.append(("EVAL", condition, line_num))
                instructions.append(("JUMP_IF_FALSE", next_else_label, line_num))
                control_flow_stack[-1] = ("elif", end_label, next_else_label, None)
            elif line.startswith("elif"):
                compile_error(line_num, raw_line, "Found 'elif' without a matching 'if' block.")
            elif line.startswith("else") and line.endswith(":") and control_flow_stack:
                _, end_label, else_label, _ = control_flow_stack[-1]
                instructions.append(("JUMP", end_label, line_num))
                if else_label:
                    instructions.append(("LABEL", else_label, line_num))
                control_flow_stack[-1] = ("else", end_label, None, None)
            elif line.startswith("else"):
                compile_error(line_num, raw_line, "Found 'else' without a matching 'if' block.")
            elif line.startswith("if ") and line.endswith(":"):
                condition = line[3:-1].strip()
                end_label = new_label()
                else_label = new_label()
                instructions.append(("EVAL", condition, line_num))
                instructions.append(("JUMP_IF_FALSE", else_label, line_num))
                control_flow_stack.append(("if", end_label, else_label, None))
                indent_stack.append(indent)
            elif line.startswith("if "):
                compile_error(line_num, raw_line, "Missing ':' at the end of the if statement.")
            elif line.startswith("while ") and line.endswith(":"):
                condition = line[6:-1].strip()
                start_label = new_label()
                end_label = new_label()
                instructions.append(("LABEL", start_label, line_num))
                instructions.append(("EVAL", condition, line_num))
                instructions.append(("JUMP_IF_FALSE", end_label, line_num))
                control_flow_stack.append(("while", end_label, None, start_label))
                indent_stack.append(indent)
            elif line.startswith("while "):
                compile_error(line_num, raw_line, "Missing ':' at the end of the while statement.")
            elif (
                "=" in line
                and not line.startswith("print")
                and not line.startswith("if")
                and not line.startswith("elif")
                and not line.startswith("while")
                and not line.startswith("#")
            ):
                var_name, value = [part.strip() for part in line.split("=", 1)]
                if not var_name.isidentifier():
                    compile_error(line_num, raw_line, f"Invalid assignment target '{var_name}'.")

                inner_value, cast_name = _unwrap_cast(value)
                if "input(" in inner_value:
                    prompt = _extract_input_prompt(inner_value)
                    instructions.append(("INPUT", prompt, line_num))
                    if cast_name:
                        instructions.append(("CAST", cast_name, line_num))
                    instructions.append(("STORE", var_name, line_num))
                else:
                    instructions.append(("PUSH", value, line_num))
                    instructions.append(("STORE", var_name, line_num))
            elif line.startswith("print(") and line.endswith(")"):
                content = line[6:-1].strip()
                args = _split_print_args(content)
                if len(args) > 1:
                    for arg in args:
                        instructions.append(("PUSH", arg.strip(), line_num))
                    instructions.append(("PRINT_MULTI", len(args), line_num))
                else:
                    instructions.append(("PUSH", content, line_num))
                    instructions.append(("PRINT", None, line_num))
            elif line.startswith("print"):
                compile_error(line_num, raw_line, 'print must use parentheses, for example: print("hello")')
            else:
                compile_error(line_num, raw_line, "Unsupported syntax.")

        while control_flow_stack:
            block_type, end_label, else_label, start_label = control_flow_stack.pop()
            indent_stack.pop()
            if block_type == "while":
                instructions.append(("JUMP", start_label, 0))
                instructions.append(("LABEL", end_label, 0))
            elif block_type in ("if", "elif"):
                if else_label:
                    instructions.append(("JUMP", end_label, 0))
                    instructions.append(("LABEL", else_label, 0))
                instructions.append(("LABEL", end_label, 0))
            elif block_type == "else":
                instructions.append(("LABEL", end_label, 0))

        return instructions


def _unwrap_cast(value):
    for cast_name in ("int", "float", "str"):
        prefix = f"{cast_name}("
        if value.startswith(prefix) and value.endswith(")"):
            inner = value[len(prefix):-1].strip()
            return inner, cast_name
    return value, None


def _extract_input_prompt(expr):
    if expr.startswith("input(") and expr.endswith(")"):
        inner = expr[6:-1].strip()
        if (inner.startswith('"') and inner.endswith('"')) or (
            inner.startswith("'") and inner.endswith("'")
        ):
            return inner[1:-1]
        return inner
    return ""


def _split_print_args(content):
    args = []
    depth = 0
    current = []
    string_delimiter = None

    for char in content:
        if string_delimiter:
            current.append(char)
            if char == string_delimiter:
                string_delimiter = None
        elif char in ('"', "'"):
            string_delimiter = char
            current.append(char)
        elif char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        args.append("".join(current).strip())

    return args


class VirtualMachine:
    def __init__(self, input_callback=None):
        self.stack = []
        self.vars = {}
        self.output = []
        self.trace = []
        self.input_callback = input_callback

    def eval_expr(self, expr):
        if not isinstance(expr, str):
            return expr

        expr = expr.strip()
        if (expr.startswith('"') and expr.endswith('"')) or (
            expr.startswith("'") and expr.endswith("'")
        ):
            return expr[1:-1]

        try:
            return int(expr)
        except ValueError:
            pass

        try:
            return float(expr)
        except ValueError:
            pass

        try:
            return eval(expr, {"__builtins__": {}}, dict(self.vars))
        except Exception:
            return expr

    def run(self, instructions):
        labels = {}
        for index, instruction in enumerate(instructions):
            if instruction[0] == "LABEL":
                labels[instruction[1]] = index

        instruction_index = 0
        step = 0

        while instruction_index < len(instructions):
            op, value, *rest = instructions[instruction_index]
            line_num = rest[0] if rest else 0
            next_index = instruction_index + 1

            try:
                if op == "PUSH":
                    self.stack.append(self.eval_expr(value))
                elif op == "STORE":
                    if self.stack:
                        self.vars[value] = self.stack.pop()
                elif op == "PRINT":
                    output_value = self.stack.pop() if self.stack else ""
                    self.output.append(str(output_value))
                elif op == "PRINT_MULTI":
                    values = []
                    for _ in range(value):
                        values.append(str(self.stack.pop() if self.stack else ""))
                    values.reverse()
                    self.output.append(" ".join(values))
                elif op == "CAST":
                    if self.stack:
                        top = self.stack.pop()
                        if value == "int":
                            self.stack.append(int(float(top)))
                        elif value == "float":
                            self.stack.append(float(top))
                        elif value == "str":
                            self.stack.append(str(top))
                        else:
                            self.stack.append(top)
                elif op == "INPUT":
                    if self.input_callback:
                        user_input = self.input_callback(value)
                        if user_input is None:
                            return {
                                "needs_input": True,
                                "input_prompt": value,
                                "output": "\n".join(self.output),
                                "trace": list(self.trace),
                            }
                    else:
                        user_input = ""
                        self.output.append(f"[Input needed: {value}]")
                    self.stack.append(user_input)
                elif op == "EVAL":
                    self.stack.append(bool(self.eval_expr(value)))
                elif op == "JUMP_IF_FALSE":
                    condition = self.stack.pop() if self.stack else False
                    if not condition and value in labels:
                        next_index = labels[value]
                elif op == "JUMP":
                    if value in labels:
                        next_index = labels[value]
                elif op != "LABEL":
                    raise BytecodeRuntimeError("Unknown opcode.", line_num, op, value)
            except BytecodeRuntimeError:
                raise
            except Exception as exc:
                raise BytecodeRuntimeError(str(exc), line_num, op, value) from exc

            self.trace.append({
                "step": step,
                "op": op,
                "val": value,
                "line": line_num,
                "stack": list(self.stack),
                "vars": dict(self.vars),
            })
            step += 1
            instruction_index = next_index

        return "\n".join(self.output), self.trace
