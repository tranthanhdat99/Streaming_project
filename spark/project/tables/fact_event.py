from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    md5,
    when,
    lit,
    concat_ws,
    regexp_extract
)
from pyspark.sql.types import IntegerType

from udf.ip2location_udf import (
    ip2location_city_udf,
    ip2location_country_udf,
    ip2location_region_udf
)

from udf.referrer_udf import extract_referrer_name_udf
from udf.user_agent_udf import os_udf, browser_udf

def get_fact_event(df: DataFrame) -> DataFrame:

    # event_id
    df0 = df.withColumnRenamed("_id", "event_id")

    # store_id
    df1 = df0.withColumn("store_id", col("store_id").cast(IntegerType()))

    # referrer_id
    df2 = df1.withColumn(
        "referrer_name",
        extract_referrer_name_udf(col("referrer_url"))
    ).withColumn(
        "referrer_key",
        when(col("referrer_name").isNull(), lit("Unknown"))
        .otherwise(col("referrer_name"))
    ).withColumn(
        "referrer_id",
        md5(col("referrer_key"))
    ).drop("referrer_name", "referrer_key")

    # location_id
    df3 = (
        df2
        .withColumn("city", ip2location_city_udf(col("ip")))
        .withColumn("region", ip2location_region_udf(col("ip")))
        .withColumn("country", ip2location_country_udf(col("ip")))
        .withColumn(
            "loc_key",
            concat_ws("_", col("city"), col("region"), col("country"))
        )    
        .withColumn("location_id", md5(col("loc_key")))
        .drop("city", "region", "country", "loc_key")
    )

    # time_id
    df4 = df3.withColumn(
        "time_id",
        when(col("local_time").isNull() | (col("local_time") == ""), lit("Unknown"))
        .otherwise(col("local_time"))
    )

    # os_id
    df5 = df4.withColumn(
        "os_name",
        os_udf(col("user_agent"))
    ).withColumn(
        "os_id",
        md5(col("os_name"))
    ).drop("os_name")

    # browser_id
    df6 = df5.withColumn(
        "browser_name",
        browser_udf(col("user_agent"))
    ).withColumn(
        "browser_id",
        md5(col("browser_name"))
    ).drop("browser_name")

    # product_id
    df7 = df6.withColumn(
        "product_id",
        when(col("product_id").isNull() | (col("product_id") == ""), lit("Unknown"))
        .otherwise(col("product_id"))
    )

    # Final table
    return df7.select(
        "event_id",
        "time_id",
        "product_id",
        "store_id",
        "location_id",
        "referrer_id",
        "browser_id",
        "os_id",
        "collection"
    )



