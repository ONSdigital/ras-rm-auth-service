# ras-rm-auth-service

An API for the ras-rm services that handles account management for respondents only

## Setup

Based on python 3.9

Use [Pyenv](https://github.com/pyenv/pyenv) to manage installed Python versions

Install dependencies to a new virtual environment using [Pipenv](https://docs.pipenv.org/)

```bash
pip install -U pipenv
pipenv install
```

## Developing

Run the tests

```bash
make test
```

Run the server

```bash
make start
```

## Environment Variables

* `LOGGING_LEVEL`: Logging level, defaults to INFO
* `DATABASE_URI`: Defaults to "postgresql://postgres:postgres@localhost:6432/postgres"
* `SECURITY_USER_NAME`: Basic http auth username
* `SECURITY_USER_PASSWORD`: Basic http auth password
