FROM node:20-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       python3 python3-pip python3-venv nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

ENV EHRGYM_SERVER_URL=http://127.0.0.1:8000 \
    PLAYWRIGHT_HEADLESS=true \
    OPENENV_DEFAULT_WAIT_MS=350 \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

RUN npm install \
    && python3 -m venv /app/.venv \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && python3 -m playwright install --with-deps chromium \
    && npx prisma generate \
    && npx prisma db push \
    && npx prisma db seed \
    && npm run build:ehr

EXPOSE 3000 8000
ENTRYPOINT ["./docker/entrypoint.sh"]
