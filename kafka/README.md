# Kafka End‑to‑End Pipeline

A Python pipeline that ingests messages from a source Kafka topic to “intermediate” topic of local Kafka cluster, and then writes every message into MongoDB for durable storage.

---

## Overview

- **Stage 1:** `mes_producer.py`  
  • Connects to an external/source Kafka cluster  
  • Reads from `topics.source`  
  • Produces each record unchanged into the local `topics.intermediate`

- **Stage 2:** `mes_consumer.py`  
  • Connects to the local Kafka cluster  
  • Reads from `topics.intermediate`  
  • Parses JSON payloads and inserts documents into MongoDB

---

## Prerequisites

- Docker & Docker Compose  
- Python 3.8+ with `confluent_kafka` & `pymongo` libraries  
- A running MongoDB instance  
- Network access (SASL credentials) to source Kafka brokers

---

## Project Structure
```bash
kafka/
├── setup/kafka/  
│   └── docker-compose.yml    # Kafka brokers & AKHQ UI  
├── config/  
│   ├── settings.conf         # broker URLs, topics, MongoDB, logging  
│   └── kafka_server_jaas.conf  
├── srcs/  
│   ├── mes_producer.py       # Stage 1: Kafka → intermediate topic  
│   └── mes_consumer.py       # Stage 2: intermediate → MongoDB  
└── utils/  
    ├── config.py             # loads settings.conf & env overrides  
    └── logging_utils.py      # rotating‑file logger setup
```

## Quick Start
Run **all commands from the `kafka/` root folder**:

1. **Configure** broker addresses & MongoDB in `config/settings.conf`.
2. **Create network**
   ```bash
   docker network create streaming-network --driver bridge
   ```
4. **Launch Kafka cluster**:
   ```bash
   docker-compose -f setup/kafka/docker-compose.yml up -d
   ```
6. **Run Producer** (in other shells):
   ```bash
   python srcs/mes_producer.py
   ```
5. **Run Consumer** (in other shells):
   ```bash
   python srcs/mes_consumer.py
   ```

