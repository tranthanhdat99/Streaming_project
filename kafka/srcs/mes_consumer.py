import os
import json
from confluent_kafka import Consumer, KafkaException, KafkaError
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from utils.config import MONGODB, LOCAL_KAFKA, TOPICS
from utils.logging_utils import get_logger

# Initialize logger for MongoDB consumer
consumer_logger = get_logger("MongoConsumer", dir_key='consumer_2', file_key='consumer_2')


def connect_mongo():
    """
    Establish connection to MongoDB and return (client, collection).
    """
    try:
        client = MongoClient(
            MONGODB['uri'],
            serverSelectionTimeoutMS=MONGODB['serverSelectionTimeoutMS']
        )
        db = client[MONGODB['database']]
        coll = db[MONGODB['collection']]
        consumer_logger.info("Connected to MongoDB.")
        return client, coll
    except PyMongoError as e:
        consumer_logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def create_kafka_consumer():
    """
    Initialize and subscribe Kafka consumer to intermediate topic.
    """
    consumer = Consumer(LOCAL_KAFKA)
    consumer.subscribe([TOPICS['intermediate']])
    consumer_logger.info(f"Subscribed to intermediate topic '{TOPICS['intermediate']}'")
    return consumer


def process_messages():
    """
    Poll messages from Kafka and insert into MongoDB.
    """
    mongo_client, collection = connect_mongo()
    consumer = create_kafka_consumer()

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

            try:
                # Decode and parse JSON
                payload = msg.value().decode('utf-8')
                record = json.loads(payload)
                result = collection.insert_one(record)
                consumer_logger.info(
                    f"Inserted document with ID {result.inserted_id} (offset={msg.offset()})"
                )
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                consumer_logger.error(f"Skipping invalid message at offset {msg.offset()}: {e}")
            except PyMongoError as e:
                consumer_logger.exception(f"Error inserting into MongoDB: {e}")
            except Exception as e:
                consumer_logger.exception(f"Unexpected processing error: {e}")

    except KeyboardInterrupt:
        consumer_logger.info("Consumer loop interrupted by user.")
    except Exception as e:
        consumer_logger.exception(f"Fatal error in message loop: {e}")
    finally:
        consumer.unsubscribe()
        consumer.close()
        mongo_client.close()
        consumer_logger.info("Consumer and MongoDB client shut down.")

if __name__ == "__main__":
    process_messages()
