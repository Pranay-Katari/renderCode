import os
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "RenderCode API is running!"

@app.route("/execute", methods=["POST"])
def execute():
    try:
        data = request.get_json()
        language = data.get("language")
        code = data.get("code")

        if not language or not code:
            return jsonify({"error": "Missing 'language' or 'code'"}), 400

        # Handle Python execution (extend for other languages later)
        if language.lower() == "python":
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_name = tmp.name

            try:
                result = subprocess.run(
                    ["python", tmp_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10  # prevent infinite loops
                )
                return jsonify({
                    "run": {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "exit_code": result.returncode
                    }
                })
            finally:
                os.remove(tmp_name)

        return jsonify({"error": f"Language '{language}' not supported yet"}), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
