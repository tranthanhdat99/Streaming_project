from pyspark.sql.functions  import udf
from pyspark.sql.types import StringType
from user_agents import parse

def _extract_os(ua_string: str) -> str:
    if not ua_string:
        return "Unknown"
    try:
        ua = parse(ua_string)
        if ua.os.family:
            fam = ua.os.family
        else: fam = "Unknown"
        return fam if fam.lower() != "other" else "Unknown"
    except Exception:
        return "Unknown"
    
def _extract_browser (ua_string: str) -> str:
    if not ua_string:
        return "Unknown"
    try:
        ua = parse(ua_string)
        if ua.browser.family:
            fam = ua.browser.family
        else: fam = "Unknown"
        return fam if fam.lower() != "other" else "Unknown"
    except Exception:
        return "Unknown"
    
os_udf = udf(_extract_os, StringType())
browser_udf = udf(_extract_browser, StringType())
