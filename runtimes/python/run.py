from fastapi import FastAPI, Request
import subprocess, sys, re, tempfile, os

app = FastAPI()

def auto_install(code: str):
    imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_]+)', code, re.MULTILINE)
    for pkg in imports:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)

@app.post("/execute")
async def execute(req: Request):
    body = await req.json()
    code = body.get("code", "")

    auto_install(code)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(code.encode())
        tmp.flush()
        result = subprocess.run([sys.executable, tmp.name], capture_output=True, text=True)
        os.unlink(tmp.name)

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }
