FROM python:3.10-slim

# Set env flags
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_NO_VENV=1

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext \
        gcc \
        libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .
