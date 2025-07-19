import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType, TimestampType, StructType, StructField, LongType, ArrayType, MapType, BooleanType, IntegerType

from utils.config import Config
from utils.logger import Log4j
from utils.schema import DF_SCHEMA
from utils.pg_writer import get_postgres_writer

from udf.ip2location_udf import ip2location_country_udf

from tables.referrer import get_referrer
from tables.store import get_store
from tables.location import get_location
from tables.time import get_time
from tables.os import get_os
from tables.browser import get_browser
from tables.product import get_product
from tables.fact_event import get_fact_event

def  foreach_batch_handler(batch_df, batch_id):
    if batch_df is None or batch_df.rdd.isEmpty():
        log.info(f"Batch {batch_id} is empty. Skipping all tables.")
        return
    
    batch_df = batch_df.persist()

    #Build each table's DataFrame by calling its transfrom function
    df_store = get_store(batch_df)
    df_referrer = get_referrer(batch_df)
    df_location = get_location(batch_df)
    df_time = get_time(batch_df)
    df_os = get_os(batch_df)
    df_browser = get_browser(batch_df)
    df_product = get_product(batch_df)
    df_event = get_fact_event(batch_df)

    #Put them into a dict
    table_to_df = {
        "public.store": df_store,
        "public.referrer": df_referrer,
        "public.location": df_location,
        "public.time": df_time,
        "public.os": df_os,
        "public.browser": df_browser,
        "public.product": df_product,
        "public.fact_event": df_event
    }

    writer(table_to_df, batch_id)

    batch_df.unpersist()


if __name__ == '__main__':
    conf = Config()
    spark_conf = conf.spark_conf
    kafka_conf = conf.kafka_conf
    pg_conf = conf.pg_conf

    spark = SparkSession.builder \
        .config(conf=spark_conf) \
        .getOrCreate()

    log = Log4j(spark)

    log.info(f"spark_conf: {spark_conf.getAll()}")
    log.info(f"kafka_conf: {kafka_conf.items()}")

    spark.sparkContext.addFile("/data/location/IP2LOCATION-LITE-DB3.IPV6.BIN")

    df = spark.readStream \
        .format("kafka") \
        .options(**kafka_conf) \
        .load()
    
    parsed = df.select(
        F.from_json(
            F.col('value').cast('string'),
            DF_SCHEMA
        ).alias('json_data')
    ).select('json_data.*')

    #parsed.printSchema()
    
    writer = get_postgres_writer(pg_conf, log)

    query = parsed \
        .writeStream \
        .foreachBatch(foreach_batch_handler) \
        .outputMode('append') \
        .trigger(processingTime="30 seconds") \
        .start()

    query.awaitTermination()
