FROM docker.io/bitnami/spark:3.5
USER root

# Note: Python dependencies will be installed at runtime inside a virtualenv
# to save image size. This means requirements.txt should be mounted or copied at runtime.

# COPY requirements.txt /tmp/requirements.txt

# RUN pip install --upgrade pip \
#  && pip install -r /tmp/requirements.txt \
#  && rm /tmp/requirements.txt

RUN mkdir -p /data && chown -R 1001:root /data
RUN mkdir -p /opt/bitnami/spark/.ivy2 && chown -R 1001:root /opt/bitnami/spark/.ivy2
USER 1001
VOLUME /data
VOLUME /opt/bitnami/spark/.ivy2