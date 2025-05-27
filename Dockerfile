FROM python:3.10-slim

# Set env flags
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .
