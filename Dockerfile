FROM python:3.11-slim-bullseye

RUN pip3 install -v "poetry==1.8.5" \
    && rm -rf /var/lib/apt/lists/* \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock *.env ./
RUN poetry install --no-dev

COPY src ./src

CMD ["python3", "src/main.py"]
