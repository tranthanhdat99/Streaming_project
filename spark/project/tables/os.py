from pyspark.sql.functions import col, md5
from udf.user_agent_udf import os_udf

def get_os(df):

    df_only = df.select("user_agent")

    # Add os_name column 
    df_with_os = df.withColumn("os_name", os_udf(col("user_agent")))

    # Remove duplicate
    df_deduped = df_with_os.dropDuplicates(["os_name"])

    # Add os_id column
    df_with_id = df_deduped.withColumn("os_id", md5(col("os_name")))

    return df_with_id.select("os_id", "os_name")
