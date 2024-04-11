# syntax=docker/dockerfile:1

FROM python:3.10-slim

WORKDIR /usr/src/blacklist

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD [ "python", "-m" , "flask", "run", "-p", "5000", "--host=0.0.0.0"]