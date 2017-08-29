from cassandra.cqlengine import connection
from flask import make_response
from flask_restful import Resource

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById
from service.common import get_user_id_from_jwt


class Me(Resource):
    def get(self):
        user_id = get_user_id_from_jwt()
        if not user_id:
            return make_response("You must send the userInfo into the header X-Endpoint-Api-Userinfo", 405)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        user = UserInfoById.filter(user_id=user_id)
        if not user:
            return make_response("User not found", 404)
        return user.get().to_object()
