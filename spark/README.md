# Spark Streaming Analytics

A real‑time data processing pipeline: Spark Structured Streaming reads customer events from local Kafka topic, applies UDF enrichments & per‑table transforms, and upserts results into PostgreSQL tables.

---

## Overview

1. **Ingest**  
   Spark reads messages from a Kafka “intermediate” topic.

2. **Transform & Enrich**  
   • JSON schema validation (`utils/schema.py`)  
   • UDFs (e.g. IP→country lookup in `udf/`)  
   • Per‑table logic in `tables/` (store, referrer, location, time, OS, browser, product, fact_event)

3. **Write**  
   JDBC upserts into Postgres via `utils/pg_writer.py` with conflict handling from `utils/table_conflict.py`.

---

## Prerequisites

- Docker & Docker Compose  (or Spark standalone)  
- Java 17 (JRE)  
- PostgreSQL instance reachable from Spark  
- Python 3.8+ dependencies (listed in `requirements.txt`)

---

## Project Structure

```bash
spark/
├── config/
│   └── settings.conf        # Spark, Kafka & Postgres parameters
│   └── log4j/properties     # Log4j config
├── setup/spark/
│   ├── Dockerfile
│   └── docker-compose.yml
├── ip2location/             # IP2LOCATION‑LITE‑DB3.IPV6.BIN
├── requirements.txt
├── srcs/
│   └── kafka_streaming.py   # Entry point for Structured Streaming job
├── udf/                     # UDF modules (e.g. IP→country)
├── tables/                  # Table‑specific transform functions
└── utils/
    ├── config.py            # Loads `config/settings.conf`
    ├── logger.py            # Log4j wrapper
    ├── pg_writer.py         # JDBC upsert utility
    ├── schema.py            # Defines message schema
    └── table_conflict.py    # ON CONFLICT clauses for upserts
```

---

## Quick Start

Run **all commands from the `spark/` root folder**:

1. **Create network**
   ```bash
   docker network create streaming-network --driver bridge
   ```
2. **Run Spark**

   2.1. **Build Spark image**  
   ```bash
   docker build -f setup/spark/Dockerfile -t unigap/spark:3.5 .
   ```
   2.2. **Create volume**
   ```bash
   docker volume create spark_data
   docker volume create spark_lib
   ```
   2.3. **Launch Spark cluster**
   ```bash
   docker compose -f setup/spark/docker-compose.yml up -d
   ```
3. **Create folder and copy IP2Location file into Spark docker**

   3.1. **Create folder**  
   ```bash
   docker exec -ti spark-spark-1 mkdir -p /data/location
   docker exec -ti spark-spark-worker-1 mkdir -p /data/location
   docker exec -ti spark-spark-worker-2 mkdir -p /data/location
   ```
   3.2. **Copy data** 
   ```bash
   docker cp ip2location/IP2LOCATION-LITE-DB3.IPV6.BIN spark-spark-1:/data/location
   docker cp ip2location/IP2LOCATION-LITE-DB3.IPV6.BIN spark-spark-worker-1:/data/location
   docker cp ip2location/IP2LOCATION-LITE-DB3.IPV6.BIN spark-spark-worker-2:/data/location
   ```
4. **Test connection to Kafka server**  
   ```bash
   telnet HOST1 PORT1
   telnet HOST2 PORT2
   telnet HOST3 PORT3 
   ```
5. **Run program**  
   ```bash
   (cd . && zip -r code.zip utils udf tables) && \
   docker container stop kafka-streaming || true && \
   docker container rm kafka-streaming || true && \
   docker run -ti --name kafka-streaming \
   --network=streaming-network \
   -p 4040:4040 \
   -v ./:/spark \
   -v spark_lib:/opt/bitnami/spark/.ivy2 \
   -v spark_data:/data \
   -e KAFKA_SASL_JAAS_CONFIG='org.apache.kafka.common.security.plain.PlainLoginModule required username="kafka" password="UnigapKafka@2024";' \
   -e PYSPARK_DRIVER_PYTHON='python' \
   -e PYSPARK_PYTHON='./environment/bin/python' \
   unigap/spark:3.5 bash -c "python -m venv pyspark_venv && \
   source pyspark_venv/bin/activate && \
   pip install -r /spark/requirements.txt && \
   venv-pack -o pyspark_venv.tar.gz && \
   spark-submit \
   --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.7.3 \
   --archives pyspark_venv.tar.gz#environment \
   --py-files /spark/code.zip \
   /spark/srcs/kafka_streaming.py"
   ```

