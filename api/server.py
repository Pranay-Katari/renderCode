from fastapi import FastAPI, Request
import httpx

app = FastAPI()

RUNTIMES = {
    "python": "http://python:8080/execute",
    "node": "http://node:8080/execute",
    "java": "http://java:8080/execute",
    "cpp": "http://cpp:8080/execute",
}

@app.post("/execute")
async def execute(req: Request):
    body = await req.json()
    language = body.get("language")
    code = body.get("code")

    if language not in RUNTIMES:
        return {"error": f"Unsupported language: {language}"}

    async with httpx.AsyncClient() as client:
        resp = await client.post(RUNTIMES[language], json={"code": code})
        return resp.json()