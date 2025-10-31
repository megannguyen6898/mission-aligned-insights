FROM python:3.11

# 1) Install system dependencies (curl for healthcheck + WeasyPrint stack)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    curl \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    fonts-liberation \
    shared-mime-info \
    libjpeg62-turbo \
  && rm -rf /var/lib/apt/lists/*

# 2) Set env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 3) Install Python deps first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy the rest of the code
COPY . .

# 5) Default CMD (overridden by worker in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY scripts ./scripts
RUN chmod +x ./scripts/entrypoint.sh
ENTRYPOINT ["./scripts/entrypoint.sh"]
