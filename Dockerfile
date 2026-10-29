FROM python:3.15.2-alpine@sha256:20a82dbc2783112ddb91d1534603f802d222a3e63e593cd002eb2ac534e70211

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
