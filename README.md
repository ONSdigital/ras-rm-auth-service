# ras-rm-auth-service

An API for the ras-rm services that handles account management for respondents only

## Setup

Based on python 3.11

Use [Pyenv](https://github.com/pyenv/pyenv) to manage installed Python versions

Install dependencies to a new virtual environment using [Pipenv](https://docs.pipenv.org/)

```bash
pip install -U pipenv
make build
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

## Additional Note for Devs:
There are two flags i.e. `mark_for_deletion` which is a soft delete flag for the account, whereas `force_delete` is a
hard delete. These names are confusing and is going to be amended in next iteration.
Any deletion done via ROps or Frontstage will be considered as hard delete and `force_delet` feature flag will be updated.
