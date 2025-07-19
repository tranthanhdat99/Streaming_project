from pyspark.sql import DataFrame
from pyspark.sql.functions import col, md5, when, lit

from udf.referrer_udf import extract_referrer_name_udf

def get_referrer(df: DataFrame) -> DataFrame:

    # 0) Select  column 'referrer_url' only
    df_only = df.select("referrer_url")
    
    # 1) Extract domain (protocol+host) from "referrer_url"
    df_with_name = df_only.withColumn(
        "referrer_name",
        extract_referrer_name_udf(col("referrer_url"))
    )

    # 2) Deduplicate on referrer_name, this also collapses multiple NULLs into one
    df_deduped = df_with_name.dropDuplicates(["referrer_name"])

    # 3) Compute referrer_id:
    #    - If referrer_name IS NULL, assign MD5("null") as the ID.
    #    - Otherwise, use MD5(referrer_name).
    df_with_id = df_deduped.withColumn(
        "referrer_id",
        when(
            col("referrer_name").isNull(),
            md5(lit("Unknown"))
        ).otherwise(
            md5(col("referrer_name"))
        )
    )
    
    # 4) Select only the two columns:
    df_result = df_with_id.select("referrer_id", "referrer_name")

    return df_result