FROM python:3.9.6-slim-buster

ARG MODEL_NAME
ARG CONFIG_NAME

ENV APP_DIR=/opt/app
ENV CONFIG_NAME=${CONFIG_NAME}

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN apt-get update -qq -y \
    && mkdir -p /usr/share/man/man1 \
    && apt-get install --no-install-recommends -qq -y \
        build-essential \
        gosu \
        libpcre3 \
        libpcre3-dev \
        curl \
    && apt-get -y autoclean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_DIR}

# Install requirements
COPY requirements.txt prod-requirements.txt uwsgi.ini ./
RUN pip install --no-cache-dir \
    -r requirements.txt -r prod-requirements.txt \
    && useradd --create-home --shell /bin/bash nlp

# Download model from HuggingFace:
ENV MODEL_NAME=${MODEL_NAME}
COPY save_model.py ./
RUN python save_model.py

# Copy source code
COPY openapi_server openapi_server/

WORKDIR /
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8080

RUN echo 'uwsgi_read_timeout 300s > /etc/nginx/conf.d/custom_timeout.conf'

ENTRYPOINT ["/docker-entrypoint.sh"]

# Run server in development mode
# CMD ["python", "-m", "openapi_server"]

# Run server in production mode
CMD ["uwsgi", "--ini", "uwsgi.ini", "--lazy", "--http", ":8080"]