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
- Python dependencies installed via `requirements.txt`
- Redis & Postgres containers available on `streaming-network`

---

## 🚀 Quick Start
Run **all commands from the `airflow/` root folder:**
1. **Create network & Build docker image**
  
   1.1 **Create network**
   ```bash
   docker network create streaming-network --driver bridge
   ```
   1.2 **Build custom docker image**
   ```bash
   docker build -f setup/airflow/Dockerfile -t unigap/airflow:2.10.4 .
   ```
2. **Initializing Environment**

   2.1 **Setting the right Airflow user**

   Get user id information
   ```bash
   id -u
   ```
   Get group id of group docker:
   ```bash
   getent group docker
   ```
   Set the information obtained into 2 variables AIRFLOW_UID and DOCKER_GID in the .env file

2.2 Initialize airflow.cfg
docker compose run airflow-cli bash -c "airflow config list > /opt/airflow/config/airflow.cfg"
2.3 Initialize the database
docker compose up airflow-init
