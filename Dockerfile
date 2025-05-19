FROM python:3.11-slim
WORKDIR /app

# Poetry
RUN pip install --no-cache-dir poetry==1.8.2
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no‑root --no‑interaction --no‑ansi

# Подкопируем исходники
COPY app /app/app
COPY .env.example /app

CMD ["python", "-m", "app"]