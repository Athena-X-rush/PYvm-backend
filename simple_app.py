from flask import Flask, request, jsonify
from flask_cors import CORS
import sys, io, traceback
from vm import BytecodeCompiler, VirtualMachine

app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run_code():
    code = request.json.get("code", "")
    inputs = request.json.get("inputs", [])

    # ===== REAL PYTHON EXECUTION (FIXED INPUT) =====
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        input_queue = inputs.copy()
        input_index = 0

        def custom_input(prompt=""):
            nonlocal input_index
            if input_index < len(input_queue):
                value = input_queue[input_index]
                input_index += 1
                return value
            else:
                return ""

        namespace = {
            "input": custom_input
        }

        exec(code, namespace)
        real_out = sys.stdout.getvalue()

    except Exception as e:
        real_out = f"Error: {str(e)}\n{traceback.format_exc()}"

    finally:
        sys.stdout = old_stdout

    # Custom VM execution with input handling
    try:
        compiler = BytecodeCompiler()
        
        # Input callback function
        input_queue = inputs.copy()
        input_index = 0
        
        def handle_input(prompt):
            nonlocal input_index
            if input_index < len(input_queue):
                result = input_queue[input_index]
                input_index += 1
                return result
            else:
                return "default_input"
        
        vm = VirtualMachine(input_callback=handle_input)
        instructions = compiler.compile(code)
        vm_out, trace = vm.run(instructions)

        return jsonify({
            "output": real_out,
            "bytecode": instructions,
            "vm_trace": vm_out,
            "debug": trace,
            "status": "success"
        })

    except Exception as e:
        return jsonify({
            "output": real_out,
            "bytecode": [],
            "vm_trace": f"VM Error: {str(e)}",
            "debug": [],
            "status": "error"
        })


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)