import os
import subprocess
import tempfile
import shutil
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration


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
            return jsonify(run_python(code))
        elif lang in ["javascript", "js", "node"]:
            return jsonify(run_node(code))
        elif lang == "java":
            return jsonify(run_java(code))
        elif lang in ["cpp", "c++"]:
            return jsonify(run_cpp(code))
        else:
            return jsonify({"error": f"Language '{language}' not supported"}), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Execution timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Language Runners ----------

def run_python(code):
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

        # Auto-install missing pip module
        if "ModuleNotFoundError" in result.stderr:
            missing = parse_missing_module(result.stderr)
            if missing:
                subprocess.run([sys.executable, "-m", "pip", "install", missing])
                result = subprocess.run(
                    ["python", tmp_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
        return format_result(result)
    finally:
        os.remove(tmp_name)


def run_node(code):
    workdir = tempfile.mkdtemp()
    filepath = os.path.join(workdir, "main.js")

    with open(filepath, "w") as f:
        f.write(code)

    try:
        result = subprocess.run(
            ["node", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            cwd=workdir
        )

        # Auto-install missing npm module
        if "Error: Cannot find module" in result.stderr:
            missing = result.stderr.split("'")[1]
            subprocess.run(["npm", "init", "-y"], cwd=workdir)
            subprocess.run(["npm", "install", missing], cwd=workdir)

            result = subprocess.run(
                ["node", filepath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                cwd=workdir
            )
        return format_result(result)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def run_java(code):
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
            return format_result(compile_proc)

        result = subprocess.run(
            ["java", "-cp", os.path.dirname(tmp_name), base],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        return format_result(result)
    finally:
        for ext in [".java", ".class"]:
            try:
                os.remove(tmp_name.replace(".java", ext))
            except FileNotFoundError:
                pass


def run_cpp(code):
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
            return format_result(compile_proc)

        result = subprocess.run(
            [exe_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        return format_result(result)
    finally:
        for f in [tmp_name, exe_name]:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass


# ---------- Helpers ----------

def format_result(result):
    return {
        "run": {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    }


def parse_missing_module(stderr):
    if "No module named" in stderr:
        return stderr.split("'")[1]
    return None


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
