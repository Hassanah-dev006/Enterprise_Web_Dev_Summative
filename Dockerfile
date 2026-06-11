FROM python:3.11-slim

WORKDIR /app

# postgresql-client provides psql + pg_isready for the ETL entrypoint
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==22.0.0

COPY . .

EXPOSE 5001
# Service commands are supplied by docker-compose (etl vs. web).
