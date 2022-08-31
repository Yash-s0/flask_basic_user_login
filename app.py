# redis dekhna h
# how to create and verify bearer token


from flask import Flask, render_template
from flask_restful import Resource, Api, request
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr


app = Flask(__name__)
api = Api(app)


users = {}


dbEngine = create_engine("sqlite:///site.db")
Session = sessionmaker(bind=dbEngine)


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def _asdict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, unique=True, primary_key=True)
    username = Column(String(200), unique=True, nullable=False)
    password = Column(String(200), unique=False, nullable=False)


class HealthCheck(Resource):
    def get(self):
        return {"success": True}


class RegisterUser(Resource):
    def post(self):
        args = request.json
        username = args.get("username")
        password = args.get("password")
        hashed_pass = sha256_crypt.encrypt(password)
        # to decode the password.
        # org_pass = sha256_crypt.verify(password, hashed_pass)

        if username is None or password is None:
            return {"success": False, "message": "Missing required params"}, 400

        if username in users:
            return {"success": False, "message": "User already exists."}, 409
        # users[username] = password

        new_user = User(username=username, password=hashed_pass)
        db = Session()
        db.add(new_user)
        db.commit()

        return {
            "success": True,
            "message": "Successfull register!",
        }


class AllUsers(Resource):
    # WORKING GET ALL USERS
    def get(self):
        db = Session()
        all_users = db.query(User).all()
        all_users = [user._asdict() for user in all_users]

        return [name["username"] for name in all_users]


api.add_resource(HealthCheck, "/health_check")
api.add_resource(RegisterUser, "/register")
api.add_resource(AllUsers, "/get_all_users")


if __name__ == "__main__":
    Base.metadata.create_all(dbEngine)
    app.run(debug=True)
