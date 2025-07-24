
# Real‑Time Customer Insights for Glamira

This project demonstrates a full streaming data pipeline that captures customer interactions on the Glamira website and turns them into structured insights. It uses Apache Kafka to ingest click and view events, Spark Structured Streaming to enrich and transform data, and Airflow to orchestrate and monitor each stage.

---

## Core Capabilities

- **Event Streaming**  
  Capture every product view, add‑to‑cart, and filter action from the Glamira site in real time.

- **Data Enrichment**  
  Apply IP‑to‑location lookups, parse timestamps, and extract key fields via reusable UDFs.

- **Incremental Upserts**  
  Persist aggregated and cleaned records into PostgreSQL tables, handling conflicts gracefully.

- **Automated Monitoring & Alerts**  
  Use Airflow DAGs to run health checks on Kafka brokers, Spark cluster, and Postgres ingestion—notify Slack on any issues.

---

## Key Use Cases

1. **Live Product Popularity**  
   Maintain up‑to‑date top‑N lists of most viewed rings, necklaces, and other accessories.

2. **Geographic Trends**  
   Track visitor locations by country and city for targeted marketing and inventory planning.

3. **Store Page Performance**  
   Compare traffic across regional store pages (e.g., USA vs. Germany) to optimize localization.

4. **Operational Reliability**  
   Get immediate alerts if any component (Kafka, Spark, or Postgres) experiences downtime or lag.

---

## Architecture

```text
[ Website Events ] 
       ↓ (Kafka Source Topic)
[ Kafka Producer ] ──▶ [ Kafka Intermediate Topic ] ──▶ [ Kafka Consumer ] ──▶ MongoDB
                                                        ↓
                                             [ Spark Structured Streaming ]
                                                        ↓
                                                  PostgreSQL Tables
                                                        ↓
                                               [ Airflow Monitoring DAGs ]
                                                        ↓
                                                  Slack Notifications
```

- **Kafka**  
  Handles event ingestion and decoupling from the source website.

- **MongoDB**  
  Acts as a raw event archive for all ingested messages.

- **Spark**  
  Processes streaming data into analytical tables with UDF enrichments and upserts.

- **Airflow**  
  Orchestrates and monitors each pipeline stage, sending Slack alerts on failures.

---

## Getting Started

1. **Clone this repository**  
   ```bash
   git clone https://github.com/tranthanhdat99/glamira_streaming_pipeline.git
   cd glamira_streaming_pipeline
2. **Install prerequisites**:

     - Docker & Docker Compose
     - Python 3.8+ (with `confluent_kafka`, `pymongo`)
     - Java 17 (for Spark)
     - Running instances of MongoDB and PostgreSQL
3. **Follow each subfolder’s README** for setup and run instructions:  
   - `kafka/` – streaming and Mongo archiving  
   - `spark/` – lightweight transformations and Postgres upserts  
   - `airflow/` – simple DAGs and alerts  
4. **Configure** connection strings, credentials, and thresholds in each `config/` folder or via environment variables.
5. **Launch services**

    Launch services in the order: Kafka → Spark → Airflow
6. **Observe**
  
   - Kafka and Spark UIs for cluster health and streaming metrics
   - Airflow UI for DAG status
   - Slack for real‑time alerts
  
---

## Repository Layout
```bash
├── kafka/      Kafka cluster setup, Python producer & consumer, MongoDB archiving  
├── spark/      Spark job, UDFs, schema, PostgreSQL upserts  
├── airflow/    Airflow DAGs, alert utilities, Docker deployment  
└── README.md   Project overview and architecture
```
