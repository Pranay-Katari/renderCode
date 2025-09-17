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

        lang = language.lower()

        if lang == "python":
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
                    timeout=10
                )
                return jsonify(format_result(result))
            finally:
                os.remove(tmp_name)

        elif lang in ["javascript", "js", "node"]:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_name = tmp.name

            try:
                result = subprocess.run(
                    ["node", tmp_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                return jsonify(format_result(result))
            finally:
                os.remove(tmp_name)

        elif lang == "java":
            with tempfile.NamedTemporaryFile(mode="w", suffix=".java", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_name = tmp.name
                base = os.path.splitext(os.path.basename(tmp_name))[0]

            try:
                compile_proc = subprocess.run(
                    ["javac", tmp_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                if compile_proc.returncode != 0:
                    return jsonify(format_result(compile_proc))

                result = subprocess.run(
                    ["java", "-cp", os.path.dirname(tmp_name), base],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                return jsonify(format_result(result))
            finally:
                for ext in [".java", ".class"]:
                    try:
                        os.remove(tmp_name.replace(".java", ext))
                    except FileNotFoundError:
                        pass

        elif lang in ["c++", "cpp"]:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False) as tmp:
                tmp.write(code)
                tmp.flush()
                tmp_name = tmp.name
                exe_name = tmp_name + ".out"

            try:
                compile_proc = subprocess.run(
                    ["g++", tmp_name, "-o", exe_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                if compile_proc.returncode != 0:
                    return jsonify(format_result(compile_proc))

                result = subprocess.run(
                    [exe_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                return jsonify(format_result(result))
            finally:
                for f in [tmp_name, exe_name]:
                    try:
                        os.remove(f)
                    except FileNotFoundError:
                        pass

        return jsonify({"error": f"Language '{language}' not supported"}), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def format_result(result):
    return {
        "run": {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
