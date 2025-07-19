# Kafka End‑to‑End Pipeline

A Python pipeline that ingests messages from a source Kafka topic to “intermediate” topic of local Kafka cluster, and then writes every message into MongoDB for durable storage.

---

## 📝 Overview

- **Stage 1:** `mes_producer.py`  
  • Connects to an external/source Kafka cluster  
  • Reads from `topics.source`  
  • Produces each record unchanged into the local `topics.intermediate`

- **Stage 2:** `mes_consumer.py`  
  • Connects to the local Kafka cluster  
  • Reads from `topics.intermediate`  
  • Parses JSON payloads and inserts documents into MongoDB

---

## ⚙️ Prerequisites

- Docker & Docker Compose  
- Python 3.8+ with `confluent_kafka` & `pymongo` libraries  
- A running MongoDB instance  
- Network access (SASL credentials) to source Kafka brokers

---

## 🚀 Quick Start

1. **Configure** broker addresses & MongoDB in `config/settings.conf`.
2. **Create network**
   ```bash
   docker network create streaming-network --driver bridge
   ```
3. **Launch Kafka cluster**:
   ```bash
   docker-compose -f setup/kafka/docker-compose.yml up -d
   ```
4. **Run Producer** (in another shell):
```bash
python srcs/mes_producer.py
```
5. **Run Consumer**:
   ```bash
python srcs/mes_consumer.py
```
