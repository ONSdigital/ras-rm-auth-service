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

* `DEBUG`: Enable Django Debug Mode, defaults to "True"
* `DB_HOST`: Database host, defaults to "localhost" overridden by `VCAP_SERVICES`
* `DB_NAME`: Database name, defaults to "postgres" overridden by `VCAP_SERVICES`
* `DB_USERNAME`: Database username, defaults to "postgres" overridden by `VCAP_SERVICES`
* `DB_PASSWORD`: Database password, defaults to "postgres" overridden by `VCAP_SERVICES`
* `DB_PORT`: Database port, defaults to "6432"
* `DB_SCHEMA`: Schema to use to prevent collisions with other Django apps, defaults to "public"
* `DJANGO_SETTINGS_MODULE`: Django settings to use, should be `ras_rm_auth_service.settings.default`
