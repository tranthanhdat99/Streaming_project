import os
from confluent_kafka import Consumer, Producer, KafkaError

from utils.config import SOURCE_KAFKA, DEST_KAFKA, TOPICS
from utils.logging_utils import get_logger

consumer_logger = get_logger("ConsumerLogger", dir_key='consumer_1', file_key='consumer_1')
producer_logger = get_logger("ProducerLogger", dir_key='producer',   file_key='producer')

def create_kafka_consumer():
    """
    Create and subscribe a Kafka Consumer for the source cluster.
    """
    consumer = Consumer(SOURCE_KAFKA)
    consumer.subscribe([TOPICS['source']])
    consumer_logger.info(f"Subscribed to source topic '{TOPICS['source']}'")
    return consumer


def create_kafka_producer():
    """
    Create a Kafka Producer for the destination cluster.
    """
    producer = Producer(DEST_KAFKA)
    producer_logger.info(f"Initialized producer for topic '{TOPICS['intermediate']}'")
    return producer


def delivery_callback(err, msg):
    """
    Callback for delivery results. Logs success or failure.
    """
    if err:
        producer_logger.error(f"Delivery failed: {err}")
    else:
        producer_logger.info(
            f"Delivered to {msg.topic()}[{msg.partition()}] at offset {msg.offset()}"
        )


def replicate_messages():
    """
    Poll from source topic and forward each message to the intermediate topic.
    """
    consumer = create_kafka_consumer()
    producer = create_kafka_producer()
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    consumer_logger.info(
                        f"Reached end of partition {msg.topic()}[{msg.partition()}]"
                    )
                else:
                    consumer_logger.error(f"Consumer error: {msg.error()}")
                continue

            # Forward payload without mutation
            producer.produce(
                TOPICS['intermediate'], msg.value(), callback=delivery_callback
            )
            producer.poll(0)

    except KeyboardInterrupt:
        consumer_logger.info("Replication interrupted by user.")
    except Exception as e:
        consumer_logger.exception(f"Unexpected error in replication: {e}")
    finally:
        consumer.close()
        producer.flush()
        consumer_logger.info("Consumer and Producer have cleanly shut down.")

if __name__ == "__main__":
    replicate_messages()
