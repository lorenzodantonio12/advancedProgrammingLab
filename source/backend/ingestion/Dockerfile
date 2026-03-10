FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir requests pydantic stomp.py fastapi uvicorn sqlalchemy

COPY . .

CMD ["python", "-u", "rest_poller.py"]