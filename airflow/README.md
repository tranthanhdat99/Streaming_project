# Airflow Monitoring Orchestrator

A set of Airflow DAGs that schedule, run, and alert on Kafka, Spark, and Postgres health checks and data pipelines.

---

## 📝 Overview

- **Kafka DAG**: Monitors broker TCP health, topic availability, message throughput, and consumer lag.  
- **Spark DAG**: Checks Spark master and worker availability and resource usage.  
- **Postgres DAG**: Verifies recent data ingestion into your reporting tables.  
- Alerts are sent to Slack on failure via `include/alert_utils.py`.

---

## ⚙️ Prerequisites

- Docker & Docker Compose  
- A `.env` file at project root
- Python dependencies installed via requirements.txt
- Redis & Postgres containers available on streaming-network

---

## 🚀 Quick Start
Run **all commands from the `airflow/` root folder:**
