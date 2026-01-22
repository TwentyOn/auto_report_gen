FROM python3:11-slim as builder
WORKDIR /app
COPY requiremets.txt .
RUN pip install -r --no-cache-dir -r requiremets.txt
COPY . .