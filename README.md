# ras-rm-auth-service
[![Build Status](https://travis-ci.org/ONSdigital/ras-rm-auth-service.svg?branch=master)](https://travis-ci.org/ONSdigital/ras-rm-auth-service)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5c72e3cdb35b487ea0f462f8b3ee4606)](https://www.codacy.com/app/sdcplatform/ras-rm-auth-service?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/ras-rm-auth-service&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/ONSdigital/ras-rm-auth-service/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/ras-rm-auth-service)


A replacement for the [django-oauth2-test](https://github.com/ONSdigital/django-oauth2-test)

## Developing

Run the tests

```
make test
```

Run the server

```
make run
```

## Environment Variables

* `LOGGING_LEVEL`: Logging level, defaults to INFO
* `DATABASE_URI`: Defaults to "postgres://postgres:postgres@localhost:6432/postgres" overridden by `VCAP_SERVICES`
* `DB_POOL_SIZE`: Configure database connection pool size, defaults to 5 
* `DB_MAX_OVERFLOW`: Configure database max connection pool overflow, defaults to 10
* `SECURITY_USER_NAME`: Basic auth username
* `SECURITY_USER_PASSWORD`: Basic auth password
