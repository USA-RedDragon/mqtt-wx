FROM python:3.14.8-alpine@sha256:f6a589d43c42b9e7f7dc67a12d37132491f362859a5d750607710cc56da3bc72

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /tmp/requirements.txt

RUN apk add --virtual .build-deps \
        build-base \
    && apk add \
        bash \
    && pip install -r /tmp/requirements.txt \
    && apk del .build-deps \
    && rm -rf /tmp/* /var/cache/apk/*

COPY *.py /app/

RUN rm -f /tmp/requirements.txt

ENTRYPOINT ["python", "-m", "main"]
