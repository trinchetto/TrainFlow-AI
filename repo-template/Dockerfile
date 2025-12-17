FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir "poetry==1.8.4" \
    && poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

COPY src ./src

EXPOSE 8080

# Replace with your application's entry point
CMD ["sh", "-c", "python src/{{PACKAGE_NAME}}/main.py"]
