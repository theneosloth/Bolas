FROM python:3.7

MAINTAINER Stefan Kuznetsov (skuznetsov@posteo.net)

RUN apk add git

ADD . /bolas

WORKDIR /bolas

RUN pip install -r requirements.txt

CMD ["python", "./run.py"]
