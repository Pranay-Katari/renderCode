FROM openjdk:17-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install fastapi uvicorn

COPY run.py /app/run.py

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8080"]
