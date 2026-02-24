FROM python:3.12-slim

WORKDIR /app

# System deps for PyMuPDF + asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
RUN python -m spacy download en_core_web_sm

COPY . .

# Create local data dir (fallback); HF Spaces uses persistent /data at runtime
RUN mkdir -p /app/data /data

# HF Spaces expects port 7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
