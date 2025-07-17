# File: spark/11-kafka-streaming/tables/store.py

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, lit
from pyspark.sql.types import IntegerType

def get_store(df: DataFrame) -> DataFrame:
    
    # Select column "store_id" only
    df_only = df.select("store_id")

    # Cast store_id to Interger Type
    df_casted = df_only.withColumn("store_id", col("store_id").cast(IntegerType()))

    df_valid = df_casted.filter(col("store_id").isNotNull())

    #Create store code
    df_code = df_valid.withColumn("store_name",
        concat_ws("_", lit("store"), col("store_id"))                        
        )
    
    # Deduplicate by store_id
    df_deduped = df_code.dropDuplicates(["store_id"])

    return df_deduped.select("store_id", "store_name")



