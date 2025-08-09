from flask import Flask, request, jsonify, render_template
import sys
import io
import threading
import queue
import uuid
import time

app = Flask(__name__)

# Store active execution sessions
active_sessions = {}

class InteractiveSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.waiting_for_input = False
        self.execution_thread = None
        self.namespace = {}
        
    def custom_input(self, prompt=""):
        if prompt:
            self.output_queue.put(prompt)
        self.waiting_for_input = True
        # Wait for input from the frontend
        user_input = self.input_queue.get()
        self.waiting_for_input = False
        return user_input
    
    def custom_print(*args, **kwargs):
        # Capture print output
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        return output.getvalue()

# Genz slang → Python keyword map
slang_to_python = {
    "sus": "if",
        "nope": "else",
        "sus_else": "elif",
        "loop": "while",
        "vibe": "for",
        "snacc": "in",
        "stop_it": "break",
        "skip_it": "continue",
        "pass_it": "pass",

        # Functions & Classes
        "make": "def",
        "gang": "class",
        "return_it": "return",
        "bring": "import",
        "bring_as": "as",
        "from_place": "from",
        
        # Printing / Input
        "say": "print",
        "spill": "input",
        
        # Boolean
        "fr": "True",
        "cap": "False",
        "null": "None",
        "andalso": "and",
        "orelse": "or",
        "nah": "not",
        
        # Operators
        "maths": "+",
        "minus": "-",
        "times": "*",
        "div": "/",
        "modu": "%",
        "powah": "**",
        "is_same": "==",
        "not_same": "!=",
        "big": ">",
        "small": "<",
        "big_o_equal": ">=",
        "small_o_equal": "<=",
        
        # Loops utils
        "nums": "range",
        "length": "len",
        "add_it": "append",
        "pop_it": "pop",

        # Data structures
        "listy": "list",
        "dicty": "dict",
        "setty": "set",
        "tupley": "tuple",
        
        # With context manager
        "wit": "with",
        "as_it": "as",
        
        # Try / Except
        "try_it": "try",
        "catch_it": "except",
        "finally_it": "finally",
        "raise_it": "raise",
        
        # Misc
        "lambda_it": "lambda",
        "global_it": "global",
        "nonlocal_it": "nonlocal",
        "assert_it": "assert",
        "del_it": "del",
        "yield_it": "yield",
}

# Python error → Genz slang
def translate_error_to_genz(error_message):
    slang_map = {
        "SyntaxError": "Yo fam, that syntax is whack — fix your vibes and check your colons/brackets",
        "IndentationError": "Bro, your indents are looking sus — align them properly fr",
        "NameError": "You calling a homie that doesn't even exist — check your variable names",
        "TypeError": "Mismatched vibes fam — wrong type of data, check what you're mixing",
        "ZeroDivisionError": "Bestie, you can't flex by dividing by zero — that's not how math works",
        "IndexError": "Yo, you tried to snacc outside the bag — list index out of range",
        "KeyError": "Bruh, that key ain't in the dictionary — double check your keys",
        "AttributeError": "Chief, that object doesn't know that move — method/attribute doesn't exist",
        "ValueError": "Those vibes ain't valid fam — check your values and data types",
        "ImportError": "Can't bring that module to the party — import failed",
        "ModuleNotFoundError": "That module is nowhere to be found — check if it's installed"
    }
    
    # Check for specific error types first
    for keyword, slang in slang_map.items():
        if keyword in error_message:
            return f"{slang}\n\nOriginal error: {error_message}"
    
    # If no specific match, return generic message
    return f"Lowkey can't decode this error rn — something went wrong\n\nOriginal error: {error_message}"

# Convert Genz slang to Python code
def genz_to_python(code):
    for slang, py in slang_to_python.items():
        code = code.replace(slang, py)
    return code

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/python-to-genz")
def python_to_genz():
    return render_template("python_to_genz.html")

def execute_code_in_session(session, python_code):
    """Execute code in a session with custom input/output handling"""
    output_buffer = []
    
    def custom_print(*args, **kwargs):
        # Capture print output
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        result = output.getvalue().rstrip('\n')
        output_buffer.append(result)
        session.output_queue.put(result)
    
    def custom_input(prompt=""):
        if prompt:
            output_buffer.append(prompt)
            session.output_queue.put(prompt)
        session.waiting_for_input = True
        # Wait for input from the frontend
        user_input = session.input_queue.get()
        session.waiting_for_input = False
        return user_input
    
    # Create execution namespace with custom functions
    namespace = session.namespace.copy()
    namespace.update({
        'print': custom_print,
        'input': custom_input,
        '__builtins__': __builtins__
    })
    
    try:
        exec(python_code, namespace)
        session.namespace.update(namespace)
        return '\n'.join(output_buffer), None
    except Exception as e:
        error_msg = translate_error_to_genz(str(e))
        return '\n'.join(output_buffer), error_msg

@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    genz_code = data.get("code", "")

    if not genz_code.strip():
        return jsonify({"error": "Bruh, no code to vibe with"})

    # Translate Genz → Python
    try:
        python_code = genz_to_python(genz_code)
    except Exception as e:
        return jsonify({"error": translate_error_to_genz(str(e))})
    
    # Create new session
    session_id = str(uuid.uuid4())
    session = InteractiveSession(session_id)
    active_sessions[session_id] = session
    
    # Store execution results
    execution_result = {"output": None, "error": None}
    
    # Execute code in a separate thread
    def run_in_thread():
        try:
            output, error = execute_code_in_session(session, python_code)
            execution_result["output"] = output
            execution_result["error"] = error
        except Exception as e:
            execution_result["error"] = translate_error_to_genz(str(e))
        
        if not session.waiting_for_input:
            # Clean up session if not waiting for input
            if session_id in active_sessions:
                del active_sessions[session_id]
    
    session.execution_thread = threading.Thread(target=run_in_thread)
    session.execution_thread.start()
    
    # Wait a bit to see if we get immediate output, error, or need input
    time.sleep(0.2)
    
    # Collect any immediate output
    output_lines = []
    try:
        while True:
            line = session.output_queue.get_nowait()
            output_lines.append(line)
    except queue.Empty:
        pass
    
    response = {}
    
    # Check if there's an error from execution
    if execution_result["error"]:
        response["error"] = execution_result["error"]
        # Clean up session on error
        if session_id in active_sessions:
            del active_sessions[session_id]
    elif output_lines:
        response["output"] = '\n'.join(output_lines)
    
    if session.waiting_for_input and not execution_result["error"]:
        response["needsInput"] = True
        response["executionId"] = session_id
    else:
        # Check if thread finished
        session.execution_thread.join(timeout=0.1)
        if session_id in active_sessions and not session.waiting_for_input:
            del active_sessions[session_id]
    
    return jsonify(response)

@app.route("/input", methods=["POST"])
def handle_input():
    data = request.get_json()
    execution_id = data.get("executionId")
    user_input = data.get("input", "")
    
    if execution_id not in active_sessions:
        return jsonify({"error": "Session not found or expired"})
    
    session = active_sessions[execution_id]
    
    # Send input to the session
    session.input_queue.put(user_input)
    
    # Wait for more output or completion
    time.sleep(0.1)
    
    # Collect output
    output_lines = []
    try:
        while True:
            line = session.output_queue.get_nowait()
            output_lines.append(line)
    except queue.Empty:
        pass
    
    response = {}
    if output_lines:
        response["output"] = '\n'.join(output_lines)
    
    if session.waiting_for_input:
        response["needsInput"] = True
    else:
        # Session completed, clean up
        if execution_id in active_sessions:
            del active_sessions[execution_id]
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)