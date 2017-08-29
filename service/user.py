import base64
import json

from cassandra.cqlengine import connection
from cassandra.cqlengine.query import LWTException
from flask import make_response
from flask_restful import Resource, request

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById, UserInfoByUsername


def get_user_id_from_jwt():
    userinfo_encoded = request.headers.get("X-Endpoint-Api-Userinfo")
    userinfo = json.loads(base64.b64decode(userinfo_encoded))
    return userinfo.get("id")


class GetUser(Resource):
    def get(self, user_id):
        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        user = UserInfoById.filter(user_id=user_id)
        if not user:
            return make_response("User not found", 404)

        return user.get().to_object()


class UpdateUser(Resource):
    def put(self):
        user_id = get_user_id_from_jwt()
        if not user_id:
            return make_response("You must send the userInfo into the header X-Endpoint-Api-Userinfo", 500)

        user = request.get_json(silent=True)

        if not user:
            return make_response("Must send user information", 405)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)

        user_info = UserInfoById.objects(user_id=user_id)
        if not user_info:
            return make_response("User not found", 404)
        username = user_info.get().to_object().get('username')

        UserInfoById.objects(user_id=user_id).if_exists().update(
            email=user.get('email')
        )

        return UserInfoById.get(user_id=user_id).to_object()


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


class Me(Resource):
    def get(self):
        user_id = get_user_id_from_jwt()
        if not user_id:
            return make_response("You must send the userInfo into the header X-Endpoint-Api-Userinfo", 500)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        user = UserInfoById.filter(user_id=user_id)
        if not user:
            return make_response("User not found", 404)
        return user.get().to_object()
