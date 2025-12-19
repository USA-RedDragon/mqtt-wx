FROM python:3.14.2-alpine@sha256:7af51ebeb83610fb69d633d5c61a2efb87efa4caf66b59862d624bb6ef788345

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
