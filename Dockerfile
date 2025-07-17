FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.7.20 /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN chmod +x /app/entrypoint.sh

RUN uv sync --locked

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]