import os
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from pyspark import SparkFiles
import IP2Location

# keep a module‐level variable that will be initialized on first lookup
_ip2location_db = None

def _get_ip2location_db():
    global _ip2location_db
    if _ip2location_db is None:
        bin_path = SparkFiles.get('IP2LOCATION-LITE-DB3.IPV6.BIN')
        _ip2location_db = IP2Location.IP2Location(bin_path)
    return _ip2location_db

def _lookup_country(ip_address: str) -> str:
    """
    Given an IP address as string, return the country name,
    or None if lookup fails.
    """
    if not ip_address:
        return "Unknown"
    try:
        db = _get_ip2location_db()
        # Use the fast country-only lookup
        country =  db.get_country_long(ip_address)
        if not country:
            return "Unknown"
        return country
    except Exception:
        return "Unknown"

def _lookup_region(ip_address: str) -> str:
    if not ip_address:
        return "Unknown"
    try:
        db = _get_ip2location_db()
        region = db.get_region(ip_address)
        if not region:
            return "Unknown"
        return region
    except Exception:
        return "Unknown"

def _lookup_city(ip_address: str) -> str:
    if not ip_address:
        return "Unknown"
    try:
        db = _get_ip2location_db()
        city = db.get_city(ip_address)
        if not city:
            return "Unknown"
        return city
    except Exception:
        return "Unknown"


# Exposed Spark UDF
ip2location_country_udf = udf(_lookup_country, StringType())
ip2location_region_udf = udf(_lookup_region, StringType())
ip2location_city_udf = udf(_lookup_city, StringType())
