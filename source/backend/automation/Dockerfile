FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn requests stomp.py
COPY . .
# Il comando per far partire l'app è già nel docker-compose