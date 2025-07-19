from pyspark.sql import DataFrame
from pyspark.sql.functions import col, md5, concat_ws, when, lit

from udf.ip2location_udf import (
    ip2location_country_udf,
    ip2location_region_udf,
    ip2location_city_udf
)

def get_location(df):
    """
    Input: DataFrame `df` that has an "ip" column.
    Output: DataFrame with these 4 columns:
       - location_id   CHAR(32) = MD5(city ∥ region ∥ country)
       - city          STRING (nullable)
       - region        STRING (nullable)
       - country       STRING (nullable)
    """

    # Select the column "ip" only
    df_only = df.select("ip")

    df_with_loc = (
        df_only
        .withColumn("city", ip2location_city_udf(col("ip")))
        .withColumn("region", ip2location_region_udf(col("ip")))
        .withColumn("country", ip2location_country_udf(col("ip")))
    )

    #Deduplicate on (city, region, country):
    df_deduped = df_with_loc.dropDuplicates(["city","region","country"])

    # Build loc_key and MD5:
    df_keyed = df_deduped.withColumn(
        "loc_key",
            concat_ws("_", col("city"), col("region"), col("country"))
        )
    
    df_with_id = df_keyed.withColumn("location_id", md5(col("loc_key")))

    return df_with_id.select(
        "location_id", "city", "region", "country")


