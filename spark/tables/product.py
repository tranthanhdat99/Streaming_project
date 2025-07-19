from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col,
    md5,
    regexp_extract,
    when,
    lit
)

def get_product (df: DataFrame) -> DataFrame:

    # Select columns 'current_url' and 'collection' only
    df_filtered = df.filter(
        (col("product_id").isNotNull()) & (col("product_id") != "")
    ).select("current_url", "collection", "product_id")


    # Apply regex only when 'collection' value satisfy the condition
    pattern = r'^(?:[^/]*\/){3}(?:glamira-)?(.*?)(?:-sku.*)?\.html'
    df_raw = df_filtered.withColumn(
        "product_name_raw",
        when(
            col("collection").isin(
                "select_product_option",
                "select_product_option_quality",
                "product_detail_recommendation_visible",
                "view_product_detail",
                "product_detail_recommendation_noticed",
                "product_detail_recommendation_clicked"
            ),
        regexp_extract(col("current_url"), pattern, 1)
        ).otherwise(lit(""))
    )

    # Normalize empty or non-matching captures to "Unknown"
    df_norm = df_raw.withColumn(
        "product_name",
        when(col("product_name_raw") == "", lit("Unknown"))
        .otherwise(col("product_name_raw"))
    )

    # Deduplicate
    df_deduped = df_norm.dropDuplicates(["product_id"])

    return df_deduped.select("product_id", "product_name")

