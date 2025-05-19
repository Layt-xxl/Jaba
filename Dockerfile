FROM python:3.11-slim-bookworm AS python-base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1        \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/root/.cache/uv


FROM ghcr.io/astral-sh/uv:latest AS uv-stage

FROM python-base AS final

COPY --from=uv-stage /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./ 

RUN uv pip install --system .

COPY app/ ./app
COPY main.py ./

ENV MODEL_PATH="app/ml/weights/best.pt"

CMD ["python", "main.py"]