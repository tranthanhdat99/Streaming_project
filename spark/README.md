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

## 🚀 Quick Start

Run **all commands from the `spark/` root folder**:

1. **Build Spark image**  
   ```bash
   docker build -f setup/spark/Dockerfile -t unigap/spark:3.5 .
