from flask_restful import Resource
from cassandra.cluster import Cluster

from conf.config import CASSANDRA_HOST


class GetUser(Resource):
    def get(self, user_id):
        cluster = Cluster(CASSANDRA_HOST)
        session = cluster.connect()
        session.set_keyspace('glimpse')
        rows = session.execute("SELECT * FROM glimpse.user WHERE user_id='" + user_id + "'")
        users = []
        for user_row in rows:
            print(user_row.username, user_row.email)
            users.append(user_row)

        return users;
