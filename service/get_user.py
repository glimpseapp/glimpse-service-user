from cassandra.cqlengine import connection
from flask import make_response
from flask_restful import Resource

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById


class GetUser(Resource):
    def get(self, user_id):
        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        user = UserInfoById.filter(user_id=user_id)
        if not user:
            return make_response("User not found", 404)

        return user.get().to_object()
