FROM python:3.11-slim

WORKDIR /app
RUN pip install fastapi uvicorn httpx

COPY server.py /app/server.py

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
