from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    md5,
    to_timestamp,
    year,
    quarter,
    month,
    weekofyear,
    dayofmonth,
    hour,
    date_format,
    lit,
    when
)
from pyspark.sql.types import LongType

def get_time (df: DataFrame) -> DataFrame:
    
    df_only = df.select("time_stamp", "local_time")

    # Build time_id
    df_norm = df_only.withColumn(
        "local_time",
        when(col("local_time").isNull() | (col("local_time") == ""), lit("Unknown"))
        .otherwise(col("local_time"))
    )
    
    df_cast = df_norm.withColumn(
        "timestamp",
        col("time_stamp").cast(LongType()).cast("timestamp")
    )
    
    # parse local_time
    df_parsed = df_cast.withColumn(
        "local_ts",
        to_timestamp(col("local_time"), "yyyy-MM-dd H:mm:ss")
    )

    # Extract date parts from local_ts
    df_enriched = (
        df_parsed
        .withColumn("year", year(col("local_ts")))
        .withColumn("quarter", quarter(col("local_ts")))
        .withColumn("month", month(col("local_ts")))
        .withColumn("week", weekofyear(col("local_ts")))
        .withColumn("day", dayofmonth(col("local_ts")))
        .withColumn("hour",hour(col("local_ts")))
        .withColumn("day_of_week", date_format(col("local_ts"), "EEEE"))
        .withColumn("is_weekend",
                    when (
                        date_format(col("local_ts"), "EEEE").isin("Saturday", "Sunday"), True\
                    ).otherwise(False)
                    )
    )

    # Deduplicate on local_time
    df_deduped = df_enriched.dropDuplicates(["local_time"])

    # Return require columns
    return df_deduped.select(
        col("local_time").alias("time_id"),
        "timestamp",
        "year",
        "quarter",
        "month",
        "week",
        "day",
        "hour",
        "day_of_week",
        "is_weekend"
    )


