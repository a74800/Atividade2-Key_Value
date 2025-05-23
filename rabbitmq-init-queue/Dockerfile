# services/rabbitmq-init-queue/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY setup_queue.py .

CMD ["python", "setup_queue.py"]
