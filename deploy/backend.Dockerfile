FROM python:3.11-slim
WORKDIR /app

# psycopg needs libpq; gcc for any wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml ./pyproject.toml
COPY backend/app ./app
RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
