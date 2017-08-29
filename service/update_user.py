from cassandra.cqlengine import connection
from flask import make_response
from flask_restful import Resource, request

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById
from service.common import get_user_id_from_jwt


class UpdateUser(Resource):
    @staticmethod
    def put():
        user_id = get_user_id_from_jwt()
        if not user_id:
            return make_response("You must send the userInfo into the header X-Endpoint-Api-Userinfo", 405)

        user = request.get_json(silent=True)

        if not user:
            return make_response("Must send user information", 405)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)

        user_info = UserInfoById.objects(user_id=user_id)
        if not user_info:
            return make_response("User not found", 404)

        UserInfoById.objects(user_id=user_id).if_exists().update(
            email=user.get('email')
        )

        return UserInfoById.get(user_id=user_id).to_object()
