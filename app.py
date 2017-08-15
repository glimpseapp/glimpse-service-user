#!flask/bin/python
from flask import Flask
from flask_restful import Api

from conf.config import HTTP_HOST, HTTP_PORT
from service.healthz import Healthz
from service.user import User, CreateUser

app = Flask(__name__)
api = Api(app)

api.add_resource(Healthz, '/healthz')
api.add_resource(CreateUser, '/user')
api.add_resource(User, '/user/<user_id>')

if __name__ == '__main__':
    app.run(host=HTTP_HOST, port=HTTP_PORT)
