# Spark Streaming Analytics

A real‑time data processing pipeline: Spark Structured Streaming reads customer events from local Kafka topic, applies UDF enrichments & per‑table transforms, and upserts results into PostgreSQL tables.

---

## 📝 Overview

1. **Ingest**  
   Spark reads messages from a Kafka “intermediate” topic.

2. **Transform & Enrich**  
   • JSON schema validation (`utils/schema.py`)  
   • UDFs (e.g. IP→country lookup in `udf/`)  
   • Per‑table logic in `tables/` (store, referrer, location, time, OS, browser, product, fact_event)

3. **Write**  
   JDBC upserts into Postgres via `utils/pg_writer.py` with conflict handling from `utils/table_conflict.py`.

---

## ⚙️ Prerequisites

- Docker & Docker Compose  (or Spark standalone)  
- Java 17 (JRE)  
- PostgreSQL instance reachable from Spark  
- Python 3.8+ dependencies (listed in `requirements.txt`)

---

## 📁 Project Structure

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

## 🚀 Quick Start

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
   2.2. **Build Spark image**
   ```bash
   docker volume create spark_data
   docker volume create spark_lib
   ```
1. **Build Spark image**  
   ```bash
   docker build -f setup/spark/Dockerfile -t unigap/spark:3.5 .
