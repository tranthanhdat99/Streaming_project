from datetime import datetime, timedelta
import socket

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from airflow.models import Variable

from kafka.admin import KafkaAdminClient
from kafka import KafkaConsumer, TopicPartition

from include.alert_utils import slack_alert
from include.config import (
    KAFKA_BROKERS,
    KAFKA_CONF,
    KAFKA_CONSUMER_GROUP_ID,
    KAFKA_LAG_THRESHOLD
)

# FUNCTIONS----------------

def check_tcp_connect(**context):
    down = []
    for host, port in KAFKA_BROKERS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5s max per broker
        try:
            sock.connect((host, port))
            print(f"{host}:{port} → UP")
        except Exception as e:
            print(f"{host}:{port} → DOWN ({e})")
            down.append(f"{host}:{port}")
        finally:
            sock.close()

    if len(down) == len(KAFKA_BROKERS):
        raise AirflowException(
            f"All Kafka brokers unreachable: {', '.join(down)}"
        )

def list_user_topics():
    admin = KafkaAdminClient(**KAFKA_CONF)
    topics = admin.list_topics()
    return [t for t in topics if not t.startswith("__")]

def check_for_topics(**context):
    user_topics = list_user_topics()
    if not user_topics:
        raise AirflowException("No user topics found in Kafka cluster.")
    print(f"Found user topics: {user_topics}")

def check_throughput(**context):
    # Use metadata consumer (no group) to fetch end offsets without affecting real consumer
    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BROKERS,
        enable_auto_commit=False,
        **{k: v for k, v in KAFKA_CONF.items() if k != 'bootstrap_servers'}
    )
    topics = list_user_topics()
    total_end_offset = 0
    try:
        partitions = []
        for t in topics:
            for pid in consumer.partitions_for_topic(t) or []:
                partitions.append(TopicPartition(t, pid))
        end_offsets = consumer.end_offsets(partitions)
        total_end_offset = sum(end_offsets.values())

        prev = int(Variable.get("kafka_prev_high", default_var="0"))
        if total_end_offset <= prev:
            raise AirflowException(
                f"No new messages: previous={prev}, current={total_end_offset}"
            )
        Variable.set("kafka_prev_high", str(total_end_offset))
    finally:
        consumer.close()


def check_consumer_lag(**context):
    # Use AdminClient to read committed offsets of the real consumer group
    admin = KafkaAdminClient(**KAFKA_CONF)
    user_topics = list_user_topics()

    # fetch committed offsets for the real consumer group
    group_offsets = admin.list_consumer_group_offsets(KAFKA_CONSUMER_GROUP_ID)
    total_lag = 0
    # metadata consumer for end offsets
    meta_consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BROKERS,
        enable_auto_commit=False,
        **{k: v for k, v in KAFKA_CONF.items() if k != 'bootstrap_servers'}
    )
    try:
        for tp, committed_offset in group_offsets.items():
            if tp.topic not in user_topics:
                continue
            end_offset = meta_consumer.end_offsets([tp]).get(tp, 0)
            lag = max(end_offset - (committed_offset or 0), 0)
            total_lag += lag

        if total_lag > KAFKA_LAG_THRESHOLD:
            raise AirflowException(
                f"Total consumer lag {total_lag} exceeds threshold {KAFKA_LAG_THRESHOLD}"
            )
    finally:
        meta_consumer.close()

# DAG DEFINITION ----------------

default_args = {
    "owner": "airflow",
    "on_failure_callback": slack_alert,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id = "kafka_full_monitor",
    default_args = default_args,
    description = "Kafka end-to-end monitor: TCP, topics, throughput, and lag",
    start_date = datetime(2025, 6, 1),
    schedule_interval = "*/5 * * * *",
    catchup = False,
    max_active_runs = 1,
    tags = ["kafka", "monitoring"],
) as dag:

    tcp_health_check = PythonOperator(
        task_id = "tcp_health_check",
        python_callable = check_tcp_connect,
        provide_context = True
    )

    topic_check = PythonOperator(
        task_id = "topic_check",
        python_callable = check_for_topics,
        provide_context = True
    )

    throughput_check = PythonOperator(
        task_id = "throughput_check",
        python_callable = check_throughput,
        provide_context = True
    )

    consumer_lag_check = PythonOperator(
        task_id = "consumer_lag_check",
        python_callable = check_consumer_lag,
        provide_context = True
    )

    tcp_health_check >> topic_check >> throughput_check >> consumer_lag_check