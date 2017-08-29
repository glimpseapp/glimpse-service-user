import base64
import json

from flask import request


def get_user_id_from_jwt():
    userinfo_encoded = request.headers.get("X-Endpoint-Api-Userinfo")
    userinfo = json.loads(base64.b64decode(userinfo_encoded))
    return userinfo.get("id")
