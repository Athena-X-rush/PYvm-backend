from flask import Flask, request, jsonify
from flask_cors import CORS
from vm import BytecodeCompiler, VirtualMachine, BytecodeCompileError, BytecodeRuntimeError

app = Flask(__name__)
CORS(app)


def _format_error(prefix, exc):
    if isinstance(exc, (BytecodeCompileError, BytecodeRuntimeError)):
        return f"{prefix}: {exc}"
    return f"{prefix}: {exc}"


@app.route("/run", methods=["POST"])
def run_code():
    data = request.json or {}
    code = data.get("code", "")
    inputs = data.get("inputs", [])

    input_queue = list(inputs)
    input_index = [0]

    def input_callback(prompt=""):
        if input_index[0] < len(input_queue):
            value = input_queue[input_index[0]]
            input_index[0] += 1
            return str(value)
        return None

    try:
        compiler = BytecodeCompiler()
        instructions = compiler.compile(code)
    except Exception as exc:
        message = _format_error("Compile error", exc)
        return jsonify({
            "output": message,
            "bytecode": [],
            "vm_trace": message,
            "debug": [],
            "status": "error",
        })

    bytecode_list = [list(instr) for instr in instructions]

    try:
        vm = VirtualMachine(input_callback=input_callback)
        result = vm.run(instructions)
    except Exception as exc:
        import traceback as tb
        message = _format_error("Runtime error", exc)
        return jsonify({
            "output": f"{message}\n{tb.format_exc()}",
            "bytecode": bytecode_list,
            "vm_trace": message,
            "debug": [],
            "status": "error",
        })

    if isinstance(result, dict) and result.get("needs_input"):
        return jsonify({
            "output": result.get("output", ""),
            "bytecode": bytecode_list,
            "vm_trace": "",
            "debug": result.get("trace", []),
            "status": "needs_input",
            "input_prompt": result.get("input_prompt", "Enter input:"),
        })

    output, trace = result

    vm_trace_lines = []
    for entry in trace:
        stack_repr = entry["stack"]
        vars_repr = entry["vars"]
        vm_trace_lines.append(
            f"Step {entry['step']:>3} | Line {entry['line']:>3} | "
            f"{entry['op']:<14} {str(entry['val']):<20} | "
            f"stack={stack_repr}  vars={vars_repr}"
        )
    vm_trace_text = "\n".join(vm_trace_lines)

    return jsonify({
        "output": output,
        "bytecode": bytecode_list,
        "vm_trace": vm_trace_text,
        "debug": trace,
        "status": "success",
    })


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
