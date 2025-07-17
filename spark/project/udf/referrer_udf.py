# File: spark/11-kafka-streaming/udf/referrer_udf.py

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def extract_referrer_name(raw_url: str) -> str:
    """
    Given a raw referrer URL (e.g. "https://www.google.com/vvv/vvvv"),
    return only the protocol + host (e.g. "https://www.google.com").
    If raw_url is None or empty, return None.
    """
    if not raw_url:
        return None

    # Split on '/', e.g. ["https:", "", "www.google.com", "vvv", ...]
    parts = raw_url.split('/')
    if len(parts) >= 3 and parts[0] and parts[2]:
        return f"{parts[0]}//{parts[2]}"
    else:
        # If it doesn't have at least "protocol//host", return None
        return None

# Register as a Spark UDF returning StringType
extract_referrer_name_udf = udf(extract_referrer_name, StringType())
