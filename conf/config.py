import os

HTTP_PORT = os.getenv("HTTP_PORT", 5000)
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")

# this can be an array of IPs
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST", None)
if isinstance(CASSANDRA_HOST, str):
    CASSANDRA_HOST = CASSANDRA_HOST.split(',')
