FROM python:3.6

WORKDIR /app
COPY . /app
EXPOSE 8041
RUN pip3 install pipenv && pipenv install --system --deploy

ENTRYPOINT ["python3"]
CMD ["run.py"]
