FROM python:3.12-slim

# Prevents Python from buffering stdout/stderr — logs show up immediately
# in `docker compose logs` instead of getting stuck in a buffer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# requirements.txt uses psycopg[binary], which ships a precompiled wheel —
# no gcc/libpq-dev build step needed. (Confirmed: an earlier version of
# this Dockerfile installed them anyway, adding ~4 minutes to every build
# for nothing.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

# Hits a real, unauthenticated, lightweight page. Uses Python stdlib
# instead of curl/wget so we don't need to install either into the image.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/login/', timeout=3)" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "Django_UserHub.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
