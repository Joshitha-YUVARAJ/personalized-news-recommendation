# Multi-stage build for smaller image size (cost optimization)
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY server/requirements.txt /app/
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (from repo root context)
COPY server/app /app/server/app
COPY server/startup.sh /app/startup.sh

# Copy utils directory (needed for imports, includes dataset_loader.py)
COPY utils /app/utils

# Make startup script executable
RUN chmod +x /app/startup.sh

# Azure App Service runs on dynamic port
EXPOSE ${PORT:-8000}

# Use startup script
CMD ["/app/startup.sh"]