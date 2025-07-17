FROM docker.io/bitnami/spark:3.5
USER root

# 1) Copy in your requirements.txt
#    (make sure build context includes this file at ./requirements.txt)
#COPY ./requirements.txt /tmp/requirements.txt

# 2) Upgrade pip & install Python deps
#RUN pip install --upgrade pip \
# && pip install -r /tmp/requirements.txt \
 # clean up to keep the image small
# && rm /tmp/requirements.txt

RUN mkdir -p /data && chown -R 1001:root /data
RUN mkdir -p /opt/bitnami/spark/.ivy2 && chown -R 1001:root /opt/bitnami/spark/.ivy2
USER 1001
VOLUME /data
VOLUME /opt/bitnami/spark/.ivy2