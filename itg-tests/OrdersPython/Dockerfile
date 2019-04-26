FROM python:3.6-stretch

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "-u", "OrderConsumer.py" ]

