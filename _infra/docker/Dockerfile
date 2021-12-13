FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential curl gunicorn
RUN pip install pipenv

WORKDIR /app

COPY . /app
RUN pipenv install --deploy --system

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "4", "--timeout", "0", "run:create_app()"]


