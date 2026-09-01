FROM python:3.14.7-alpine@sha256:c6ead215bfd31f1e433d968853b7a769989117115b728874824e6c0a27cb96fc

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
