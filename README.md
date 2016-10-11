DRF JWT + Knox
==============

[![Build Status](https://travis-ci.org/ssaavedra/drf-jwt-knox.svg?branch=master)](https://travis-ci.org/ssaavedra/drf-jwt-knox)
[![codecov](https://codecov.io/gh/ssaavedra/drf-jwt-knox/branch/master/graph/badge.svg)](https://codecov.io/gh/ssaavedra/drf-jwt-knox)
[![Requirements Status](https://requires.io/github/ssaavedra/drf-jwt-knox/requirements.svg?branch=master)](https://requires.io/github/ssaavedra/drf-jwt-knox/requirements/?branch=master)

This package provides an authentication mechanism for Django REST
Framework based on [JSON Web Tokens][JWT] in the browser backed up by
[Knox][knox]-powered tokens in the database.

This package aims to take the better parts of both worlds, including:

- Expirable tokens: The tokens may be manually expired in the
  database, so a user can log out of all other logged-in places, or
  everywhere.
- Different tokens per login attempt (per user-agent), meaning that a
  user's session is tied to the specific machine and logging can be
  segregated per usage.
- JWT-based tokens, so the token can have an embedded expiration time,
  and further metadata for other applications.
- Tokens are generated via OpenSSL so that they are cryptographically more secure.
- Only the tokens' hashes are stored in the database, so that even if
  the database gets dumped, an attacker cannot impersonate people
  through existing credentials
- Other applications sharing the JWT private key can also decrypt the JWT


Usage
=====

Add this application **and knox** to `INSTALLED_APPS` in your
`settings.py`.

Then, add this app's routes to some of your `urlpatterns`.

You can use the `verify` endpoint to verify whether a token is valid
or not (which may be useful in a microservice architecture).


Tests
=====

Tests are automated with `tox` and run on Travis-CI automatically. You
can check the status in Travis, or just run `tox` from the command
line.


Contributing
============

This project uses the GitHub Flow approach for contributing, meaning
that we would really appreciate it if you would send patches as Pull
Requests in GitHub. If for any reason you prefer to send patches by email, they are also welcome and will end up being integrated here.

License
=======

This code is released under the Apache Software License Version 2.0.


[JWT]: https://github.com/jpadilla/pyjwt
[knox]: https://github.com/James1345/django-rest-knox
