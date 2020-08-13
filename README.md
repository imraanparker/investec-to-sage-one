Overview
========

Importing your 

Requirements
============

- `Python 3.6`
- `Heroku CLI` if you want to deploy to Heroku

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
uvicorn --port 5000 --host 127.0.0.1 main:app --reload
```

You can then visit the API interface at http://127.0.0.1:5000/api

Deploying to Heroku
-------------------

Create a new application in Heroku and attach the git repository.

```
heroku git:remote -a <name-of-your-app>
```

Once you are ready to deploy the application, run the following to deploy the application on Heroku

```
git push heroky master
```

You will be able to access the application via the Heroku URL and access the API on ```/api```.

The API will only work properly if the configuration is setup correctly.

Configuration
-------------

In order the application to talk to both Investec and Sage One, there are a number of config parameters that need to be set.

You can use a config file and/or environment variables to set the parameters.

To use the the config file, copy ```config_example.ini``` as ```config-local.ini``` and set the parameters in the file.
The application will automatically look for the ```config-local.ini``` and use it if it exists.

The more preferred method is to use environment variables, especially when deploying to Heroku (Config Vars).
Below is a table of the different config parameters.

**Sage**

Config File Parameter | Environment Variable | Description
--------------------- | -------------------- | ------------
username              | SAGE_USERNAME        | Your username for Sage One. Typically an email address
password              | SAGE_PASSWORD        | Your password for Sage One.
api_key               | SAGE_API_KEY         | The API Key to authenticate with the Sage One API
url                   | SAGE_URL             | The Sage One API URL.
company_id            | SAGE_COMPANY_ID      | The Company ID to use for the syncing 
bank_account_id       | SAGE_BANK_ACCOUNT_ID | The Bank Account ID under the company to use for the syncing

**Investec**

Config File Parameter | Environment Variable | Description
--------------------- | -------------------- | ------------
client_id             | INVESTEC_CLIENT_ID   | Your Investec Client ID
secret                | INVESTEC_SECRET      | Your Investec Secret
