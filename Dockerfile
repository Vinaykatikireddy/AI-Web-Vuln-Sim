FROM python:3.10-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    docker.io \
    supervisor \
    python3-dev \
    fuse-overlayfs \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpango1.0-dev \
    libharfbuzz-dev \
    shared-mime-info \
    libgdk-pixbuf2.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend /app/backend
COPY ./docker /app/docker

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]