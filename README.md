# ras-rm-auth-service

A replacement for the RM auth service

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
