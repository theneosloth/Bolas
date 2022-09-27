FROM python:3.7-slim

RUN apt-get update && apt-get install git gcc -y

ADD . /bolas

WORKDIR /bolas

RUN pip install -r requirements.txt

CMD ["python", "./run.py"]
