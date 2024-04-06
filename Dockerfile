FROM python:3.11-bullseye

WORKDIR /app

RUN apt-get update \
    && apt-get install -y git ffmpeg

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "bot"]
