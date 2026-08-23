FROM python:3.12-slim

# Prevents Python from buffering stdout/stderr — logs show up immediately
# in `docker compose logs` instead of getting stuck in a buffer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# libpq-dev + gcc: needed to build psycopg (Postgres driver) from source
# on some platforms. Removed in the same layer to keep the image small.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "Django_UserHub.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
