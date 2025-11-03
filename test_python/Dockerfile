
# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Copia requirements.txt e installa dipendenze
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'app
COPY ./app ./app

# Comando per far partire l'app FastAPI con uvicorn
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
