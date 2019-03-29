FROM python:3.6-alpine

MAINTAINER Stefan Kuznetsov (skuznetsov@posteo.net)

RUN apk add git

ADD . /bolas

WORKDIR /bolas

RUN pip install -r requirements.txt

CMD ["python", "./run.py"]
