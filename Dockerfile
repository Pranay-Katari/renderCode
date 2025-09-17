FROM python:3.11-slim
WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT}", "server:app"]
