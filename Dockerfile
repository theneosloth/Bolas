FROM python:3.6-alpine

MAINTAINER Stefan Kuznetsov (skuznetsov@posteo.net)

ADD . /bolas

WORKDIR /bolas

RUN pip install -r requirements.txt

ENV BOLAS_SECRET_TOKEN

CMD ["python", "./run.py"]
