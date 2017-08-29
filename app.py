#!flask/bin/python
from flask import Flask
from flask_restful import Api

from conf.config import HTTP_HOST, HTTP_PORT

from service.create_user import CreateUser
from service.get_user import GetUser
from service.healthz import Healthz
from service.me import Me
from service.update_user import UpdateUser

app = Flask(__name__)
api = Api(app)

api.add_resource(Healthz, '/healthz')
api.add_resource(CreateUser, '/user')
api.add_resource(GetUser, '/user/<user_id>')
api.add_resource(UpdateUser, '/user')
api.add_resource(Me, '/me')

if __name__ == '__main__':
    app.run(host=HTTP_HOST, port=HTTP_PORT)
