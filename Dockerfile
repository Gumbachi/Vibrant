FROM python:3.13-slim-bookworm

RUN apt update \
    && pip3 install uv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY src ./src

ENTRYPOINT ["uv", "run", "src/main.py"]
