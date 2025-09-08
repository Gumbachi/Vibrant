FROM python:3.12-slim-bookworm

RUN apt update && pip3 install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY src ./src

ENTRYPOINT ["uv", "run", "src/main.py"]
