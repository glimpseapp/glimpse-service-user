#!flask/bin/python
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class Healthz(Resource):
    def get(self):
        return {"status": True}


class User(Resource):
    def put(self):
        if not request.forms:
            return jsonify({"error": "You must pass the user information"})

        user = request.forms
        return user

api.add_resource(Healthz, '/healthz')
api.add_resource(User, '/')

if __name__ == '__main__':
    app.run(debug=True)
