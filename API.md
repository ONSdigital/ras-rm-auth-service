# Auth service API
 This page documents the Auth service API endpoints. Apart from the Service Information endpoint, all these endpoints 
 are secured using HTTP basic authentication.

## Service Information
* `GET /info` will return information about this service, collated from when it was last built.
 
### Example JSON Response
```json
{
  "name": "ras-rm-auth-service",
  "version": "0.1.0",
  "origin": "git@github.com:ONSdigital/ras-rm-auth-service.git",
  "commit": "dc1759cc644db1b279cb5d3ab21c29a83d33f203",
  "branch": "master",
  "built": "2018-07-04T13:18:28Z"
}
```


## create account
* `POST /api/account/create` create user account

**Required parameters:** 
`username` user's email address.
`password` user's password
 
### Example JSON Request
```json
{
  "username": "example@example.com",
  "password": "pa$$w0rd"
}
```

### Example JSON Response
```json
{
  "account": "example@example.com",
  "created": "success"
}
```

An `HTTP 201 OK` status code is returned if the request could be successfully processed.
An `HTTP 400 BAD REQUEST` status code is returned for bad request parameters.
Errors if unable to create new account.


## update account
* `PUT /api/account/create` update user account.

**Required parameters:** 
`username` user's email address.

**Optional parameters**
`account_verified` update user's verified status.
 
### Example JSON Request
```json
{
  "username": "example@example.com",
  "account_verified": "true"
}
```

### Example JSON Response
```json
{
  "account": "example@example.com",
  "updated": "success"
}
```

An `HTTP 201 OK` status code is returned if the request could be successfully processed. 
An `HTTP 400 BAD REQUEST` status code is returned for bad request parameters.
An `HTTP 401 UNAUTHORIZED` status code is returned for unauthorized user credentials.


## verify account
* `POST /api/v1/tokens` verify user account

**Required parameters:** 
`username` user's email address.
`password` user's password
 
### Example JSON Request
```json
{
  "username": "example@example.com",
  "password": "pa$$w0rd"
}
```

### Example JSON Response
```json
{
  "id": 895725, 
  "access_token": "fakefake-4bc1-4254-b43a-f44791ecec75", 
  "expires_in": 3600,
  "token_type": "Bearer", 
  "scope": "", 
  "refresh_token": "fakefake-2151-4b11-b0d5-a9a68f2c53de"
}
```

An `HTTP 201 OK` status code is returned if the request could be successfully processed. 
An `HTTP 401 UNAUTHORIZED` status code is returned for Unauthorized user credentials, unverified user and if user does not exist.
