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

CMD ["sh", "-c", "chainlit run src/trainflow_ai/chainlit_app.py --host 0.0.0.0 --port ${PORT:-8080}"]
