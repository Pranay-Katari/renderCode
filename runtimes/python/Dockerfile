FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi uvicorn

WORKDIR /app
COPY run.py /app/run.py

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8080"]
