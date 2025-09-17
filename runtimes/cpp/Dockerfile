FROM python:3.11-slim
RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install fastapi uvicorn
COPY run.py /app/run.py
EXPOSE 8080
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8080"]
