FROM python:3.11-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN prisma generate --schema=./bot/db/schema.prisma
