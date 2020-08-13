Overview
========

A sample API application to show off FastAPI.

Requirements
============

- `Python 3.8`
- `Docker`
- `Heroku CLI`

Installation
============

Development
------------

Create a virtual environment

```
 python3 -m venv /path/to/env
```

Activate the environment and install the requirements in the app folder

```
/path/to/env/bin/pip install -U -r requirements.txt
```

Run the development web server in the app folder

```
uvicorn main:app --reload
```

Production
----------

A docker container is deployed to Heroku for production use. Run the script to deploy to production.
The assumption is that you have Docker and the Heroku CLI installed.
You will need an account on Heroku in order to deploy. You might need to adapt the deploy script with your application name. 

```
./deploy.sh
```

Accessing the API
------------------

You can access the api via a browser and use the built-in Swagger interface to interact with the API.

When running in development the URL is

```
http://localhost:8000/docs
```

The production URL is

```
https://fastapi-template.herokuapp.com/docs
```

Continuous Integration
=====================

All API services are tested. ![Last Build](https://travis-ci.com/imraanparker/fastapi.svg?token=jBQpiw8ckhUhBEp5MQqf&branch=master)

Tests
======

To run the tests locally, simply run

```
pytest
```
