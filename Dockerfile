
FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt *.env ./

RUN pip3 install -r requirements.txt

COPY src ./src

CMD [ "python3", "src/main.py" ]