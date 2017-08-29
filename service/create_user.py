from cassandra.cqlengine import connection
from flask import make_response, request
from flask_restful import Resource

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById, UserInfoByUsername
from service.common import get_user_id_from_jwt


class CreateUser(Resource):
    def post(self):
        user_id = get_user_id_from_jwt()
        if not user_id:
            return make_response("You must send the userInfo into the header X-Endpoint-Api-Userinfo", 405)

        user = request.get_json(silent=True)
        if not user:
            return make_response("Must send user information", 405)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)

        if UserInfoById.filter(user_id=user_id):
            return make_response("User already exists, call the PUT API instead", 405)

        if UserInfoByUsername.filter(username=user.get('username')):
            return make_response("Username already exists, chose a different one", 405)

        UserInfoById.create(
            user_id=user_id,
            username=user.get('username'),
            email=user.get('email')
        )

        UserInfoByUsername.create(
            user_id=user_id,
            username=user.get('username'),
        )

        return UserInfoById.get(user_id=user_id).to_object()
