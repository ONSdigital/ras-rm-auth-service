# ras-rm-auth-service

[![Build Status](https://travis-ci.org/ONSdigital/ras-rm-auth-service.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-rm-auth-service)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5c72e3cdb35b487ea0f462f8b3ee4606)](https://www.codacy.com/app/sdcplatform/ras-rm-auth-service?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/ras-rm-auth-service&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/ONSdigital/ras-rm-auth-service/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-rm-auth-service)

A drop-in replacement for the [django-oauth2-test](https://github.com/ONSdigital/django-oauth2-test)

## Setup

Based on python 3.6

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
* `DATABASE_URI`: Defaults to "postgresql://postgres:postgres@localhost:6432/postgres" overridden by `VCAP_SERVICES`
* `DB_POOL_SIZE`: Configure database connection pool size, defaults to 5
* `DB_MAX_OVERFLOW`: Configure database max connection pool overflow, defaults to 10
* `SECURITY_USER_NAME`: Basic auth username
* `SECURITY_USER_PASSWORD`: Basic auth password
