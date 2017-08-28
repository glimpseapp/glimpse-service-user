import base64
import json

from cassandra.cqlengine import connection
from cassandra.cqlengine.query import LWTException
from flask import make_response
from flask_restful import Resource, request

from conf.config import CASSANDRA_HOSTS, USER_KEYSPACE
from model.user import UserInfoById, UserInfoByUsername


class User(Resource):
    def get(self, user_id):
        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        user = UserInfoById.get(user_id=user_id).to_object()
        if not user:
            return make_response("User not found", 404)

        return user

    def put(self, user_id):
        user = request.get_json(silent=True)
        if not user:
            return make_response("Must send user information", 500)

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)

        try:
            UserInfoById.objects(user_id=user_id).if_exists().update(
                username=user.get('username'),
                email=user.get('email')
            )

            UserInfoByUsername.objects(user_id=user_id).delete()
            UserInfoByUsername.create(
                user_id=user_id,
                username=user.get('username')
            )

            return UserInfoById.get(user_id=user_id).to_object()

        except LWTException as e:
            # handle failure case
            print(e)
            pass


class CreateUser(Resource):
    def post(self):
        user = request.get_json(silent=True)
        if not user:
            return make_response("Must send user information", 500)

        user_id = user.get("user_id")

        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
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
        user_id = self.get_user_id_from_jwt()
        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        user = UserInfoById.get(user_id=user_id).to_object()
        if not user:
            return make_response("User not found", 404)
        return user

    def get_user_id_from_jwt(self):
        userinfo_encoded = request.headers.get("X-Endpoint-Api-Userinfo")
        userinfo = json.loads(base64.b64decode(userinfo_encoded))
        return userinfo.get("id")
