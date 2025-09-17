from fastapi import FastAPI, Request
import subprocess
import os
import uuid

app = FastAPI()

@app.post("/execute")
async def execute_code(request: Request):
    body = await request.json()
    code = body.get("code", "")

    file_id = str(uuid.uuid4())
    source_file = f"/app/{file_id}.java"
    class_file = f"/app/{file_id}.class"

    with open(source_file, "w") as f:
        f.write(code)

    try:
        compile_proc = subprocess.run(
            ["javac", source_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        if compile_proc.returncode != 0:
            return {"stdout": "", "stderr": compile_proc.stderr}

        run_proc = subprocess.run(
            ["java", "-cp", "/app", file_id],
            capture_output=True,
            text=True,
            timeout=5
        )
#nf
        return {"stdout": run_proc.stdout, "stderr": run_proc.stderr}

    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out"}
    finally:
        if os.path.exists(source_file):
            os.remove(source_file)
        if os.path.exists(class_file):
            os.remove(class_file)
