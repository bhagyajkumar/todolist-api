FROM python:3.9

ARG SECRET_KEY=560b4ae9522e4c82936efc2b8c310b4e 

WORKDIR /code
 
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY ./app /code/app
 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

