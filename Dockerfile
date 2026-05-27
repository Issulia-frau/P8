FROM python:3.11-slim

WORKDIR /app

# Dépendances système utiles
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt .

# Installer dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Port FastAPI
EXPOSE 8000

# Lancer API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]