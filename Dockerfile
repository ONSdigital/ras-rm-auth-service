FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential curl
RUN pip install pipenv

WORKDIR /app
EXPOSE 8041
ENV GUNICORN_WORKERS 9
CMD ["sh", "docker-entrypoint.sh"]

HEALTHCHECK --interval=1m30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8041/info || exit 1

COPY . /app
RUN pipenv install --deploy --system


