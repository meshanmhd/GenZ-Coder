from flask import Flask, render_template, request, jsonify
import subprocess
import sys
from translator import genz_to_python

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    genz_code = request.json.get('code', '')

    # Convert GenZ slang to Python
    python_code = genz_to_python(genz_code)

    try:
        # Run the Python code safely
        result = subprocess.run(
            [sys.executable, "-c", python_code],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        output = "⏳ Your code took too long, bestie!"
    except Exception as e:
        output = f"Error: {e}"

    return jsonify({
        "python_code": python_code,
        "output": output
    })

if __name__ == "__main__":
    app.run(debug=True)
