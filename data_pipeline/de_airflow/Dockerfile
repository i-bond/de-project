# First-time build can take upto 10 mins.

FROM apache/airflow:2.2.3

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install vim nano jq jo -qqq
# git gcc g++ -qqq

# Ref: https://airflow.apache.org/docs/docker-stack/recipes.html

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

ARG CLOUD_SDK_VERSION=369.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk

ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

# Installing gcloud
RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

# Installing gcloud beta commands / view installed
# gcloud version
# gcloud components install beta --quiet
# gcloud components list --only-local-state
# gcloud auth login --cred-file=$GOOGLE_APPLICATION_CREDENTIALS --project=de-zoomcamp-10


# Kaggle JSON - create as root and grant access to all
ARG NAME
ARG KEY
ENV KAGGLE_NAME=$NAME
ENV KAGGLE_KEY=$KEY

RUN jo -p username=$KAGGLE_NAME key=$KAGGLE_KEY > kaggle.json \
    && mkdir /home/airflow/.kaggle \
    && cp kaggle.json /home/airflow/.kaggle \
    && chmod 777 /home/airflow/.kaggle/kaggle.json


COPY scripts scripts
RUN chmod +x scripts

WORKDIR $AIRFLOW_HOME
USER $AIRFLOW_UID

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt









