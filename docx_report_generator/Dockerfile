FROM python:3.11-alpine AS builder

# зависимости для установки psycopg2
RUN apk add --no-cache build-base libpq libpq-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]