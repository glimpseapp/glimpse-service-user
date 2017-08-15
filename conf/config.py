import os

HTTP_PORT = os.getenv("HTTP_PORT", 5000)
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")

# this can be an array of IPs
CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", None)
if isinstance(CASSANDRA_HOSTS, str):
    CASSANDRA_HOSTS = CASSANDRA_HOSTS.split(',')

USER_KEYSPACE = "user"