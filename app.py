from flask import Flask
from flask_restful import Resource, Api, request

from sqlalchemy.sql import func

# from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)


# db = SQLAlchemy(app)


users = {}


# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

# db.create_all()


# class Profile(db.Model):
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     user_id = db.Column(db.String(200), primary_key=True, unique=True, nullable=False)
#     password = db.Column(db.String(200), unique=False, nullable=False)

#     def __init__(self, user_id, password):
#         self.user_id = user_id
#         self.password = password


class HealthCheck(Resource):
    def get(self):
        return {"success": True}


class RegisterUser(Resource):
    def post(self):
        args = request.json
        user_id = args.get("user_id")
        password = args.get("password")
        if user_id is None or password is None:
            return {"success": False, "message": "Missing required params."}, 400
        if user_id in users:
            return {"success": False, "message": "User already exists."}, 409
        users[user_id] = password
        return {"success": True, "message": "Successfull register!"}


class AllUsers(Resource):
    def get(self):
        return users


api.add_resource(HealthCheck, "/health_check")
api.add_resource(RegisterUser, "/register")
api.add_resource(AllUsers, "/get_all_users")


if __name__ == "__main__":
    app.run(debug=True)
