from pyspark.sql.functions import col, md5
from udf.user_agent_udf import browser_udf

def get_browser(df):

    df_only = df.select("user_agent")

    # Add browser_name column 
    df_with_br = df.withColumn("browser_name", browser_udf(col("user_agent")))

    # Remove duplicate
    df_deduped = df_with_br.dropDuplicates(["browser_name"])

    # Add browser_id column
    df_with_id = df_deduped.withColumn("browser_id", md5(col("browser_name")))

    return df_with_id.select("browser_id", "browser_name")
