FROM faizanbashir/python-datascience:3.6

MAINTAINER Nikhil Goenka "nikhil.goenka@dynatrace.com"

RUN apk --no-cache add python3-dev musl-dev linux-headers g++

ENV PATH="/scripts:${PATH}"
COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN pip3 install Cython

RUN mkdir /app
COPY ./app /app
WORKDIR /app
COPY ./scripts /scripts

RUN chmod +x /scripts/*
EXPOSE 8090

WORKDIR scripts
WORKDIR /app
CMD ["entrypoint.sh"]
