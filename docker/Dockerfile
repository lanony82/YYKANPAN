FROM python:3.13-slim

LABEL maintainer="yykanpan" \
      description="YYKANPAN stock tracker — web dashboard + scheduled data collection"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# Install cron (for scheduled collection)
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir akshare flask pandas yfinance

# Copy application code
COPY src/ ./src/
COPY static/ ./static/
COPY watchlist_cn_sample.json ./watchlist_cn_sample.json

# Prepare data & log directories
RUN mkdir -p /app/data /app/logs

# Copy entrypoint
COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# If user doesn't mount a watchlist, fall back to sample
RUN cp watchlist_cn_sample.json watchlist_cn.json

EXPOSE 5000

VOLUME ["/app/data"]

ENTRYPOINT ["/docker-entrypoint.sh"]
