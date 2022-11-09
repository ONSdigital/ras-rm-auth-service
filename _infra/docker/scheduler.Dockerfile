FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential curl
RUN pip install pipenv

WORKDIR /app

COPY . /app
RUN pipenv install --deploy --system
CMD ["python", "scheduler.py"]
