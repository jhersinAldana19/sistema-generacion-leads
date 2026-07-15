FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Playwright solo se usa en backend/spike/ (scripts de validacion, no en
# produccion) -- no se instala Chromium aqui para no inflar la imagen.

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000

# entrypoint.sh corre las migraciones de Alembic antes de levantar uvicorn.
CMD ["./entrypoint.sh"]
