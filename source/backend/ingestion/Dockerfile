# 1. Usa un'immagine Python leggera (Slim)
FROM python:3.12-slim

# 2. Imposta la cartella di lavoro dentro il container
WORKDIR /app

# 3. Copia il file dei requisiti (se lo hai) o installa direttamente
# In questo caso installiamo le librerie che abbiamo usato finora
RUN pip install --no-cache-dir requests pydantic stomp.py fastapi uvicorn sqlalchemy

# 4. Copia tutto il contenuto della cartella locale 'ingestion' dentro '/app' nel container
COPY . .

# 5. Comando per avviare il tuo poller
# Usiamo -u (unbuffered) per vedere i print nel terminale di Docker in tempo reale
CMD ["python", "-u", "rest_poller.py"]