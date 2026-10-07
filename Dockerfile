FROM python:3.12-alpine

WORKDIR /app
COPY server.py /app/server.py
COPY index.html /app/public/index.html

RUN mkdir -p /data && adduser -D -H -u 10001 gameuser && chown -R gameuser:gameuser /app /data
USER gameuser

ENV HOST=0.0.0.0 \
    PORT=8080 \
    PUBLIC_DIR=/app/public \
    DATA_DIR=/data \
    LEADERBOARD_PASSWORD=RACK \
    PYTHONUNBUFFERED=1

EXPOSE 8080
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O - http://127.0.0.1:8080/healthz >/dev/null || exit 1
CMD ["python", "/app/server.py"]
