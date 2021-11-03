# todolist-api

This is a simple api made with intention for learning frontend.

## Key Features
#
    * Covers Authentication
    * Refresh tokens
    * One click deploy to heroku

## Deployment Options
#  
### Heroku

The easiest deploying option is to use the deploy to heroku button. it configures everything including secret_keys and database urls

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Deploy directly

First create a virtual environment
```
python -m venv venv
```
Activate te virtual environmet
```
. venv/bin/activate
```
Install the dependencies
```
pip install -r requirements.txt
```

Run the server using 

```
uvicorn app:app
```

