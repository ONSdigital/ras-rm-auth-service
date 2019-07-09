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

This endpoint came about from the old oauth2 auth service this service is replacing.  In that service, you hit the endpoint
with the credentials and you got oauth tokens in the response.  To hasten the changeover, this endpoint was left as is, but instead
of it returning tokens (that weren't being used by anything), we give a response with a status code of 204 to say that it was successful
but we don't need to give anything back to you.

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

An `HTTP 204 NO CONTENT` status code is returned if the request could be successfully processed and the user credentials are correct
An `HTTP 400 BAD REQUEST` status code is returned if the request is missing any parameters
An `HTTP 401 UNAUTHORIZED` status code is returned for Unauthorized user credentials, unverified user and if user does not exist.
