from cassandra.cqlengine import connection
from flask import make_response, request
from flask_restful import Resource

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById


class GetUsers(Resource):
    @staticmethod
    def post():

        data = request.get_json(silent=True)
        user_ids = data.get("user_ids")
        if not user_ids:
            return make_response("You must send the user_ids parameter, formatted as a list of user_id", 405)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)

        users = UserInfoById.filter(user_id__in=user_ids)

        user_list = []
        for userfriend_row in users:
            user_list.append(userfriend_row.to_object())

        return {
            "results": users.count(),
            "users": user_list
        }
