from flask import Flask, render_template
from flask_restful import Resource, Api, request
from passlib.hash import sha256_crypt
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import datetime
import jwt


app = Flask(__name__)
api = Api(app)
SECRET_KEY = "mysecret"


dbEngine = create_engine("sqlite:///site.db")
Session = sessionmaker(bind=dbEngine)


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=60),
            "iat": datetime.datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        print(e)


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=["HS256"])
        return {"success": True, "username": payload["sub"]}
    except jwt.ExpiredSignatureError:
        return {"success": False, "message": "Signature expired. Please log in again."}
    except jwt.InvalidTokenError:
        return {"success": False, "message": "Signature expired. Please log in again."}


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

        if username is None or password is None:
            return {"success": False, "message": "Missing required params"}, 400
        db = Session()

        user = db.query(User).filter_by(username=username).first()
        if user:
            return {"success": False, "message": "User already exists."}, 409

        new_user = User(username=username, password=hashed_pass)

        db.add(new_user)
        db.commit()
        db.close()

        return {
            "success": True,
            "message": "Successfull register!",
        }


class LogInUser(Resource):
    def post(self):
        data = request.get_json()
        username = data["username"]
        password_login = data["password"]

        db = Session()

        user = db.query(User).filter_by(username=username).first()
        if not user:
            return {"success": False, "message": "User does not exist."}

        verify_password = sha256_crypt.verify(password_login, user.password)

        if not verify_password:
            return {"success": False, "message": "Wrong password."}

        bearer_token = encode_auth_token(user.username)
        print(bearer_token)
        db.close()
        return {"succes": True, "bearer_token": bearer_token}


class UserInfo(Resource):
    # WORKING GET ALL USERS
    # DO NOT CHANGE ANYTHING
    def get(self):
        token = request.headers.get("Authorization")
        if token is None:
            return {"success": False, "message": "Session expried, please login"}, 404

        bearer_token = token.split("Bearer ")[1]
        verify = decode_auth_token(bearer_token)
        if "success" in verify and verify["success"] is False:
            return verify

        db = Session()
        user = db.query(User).filter_by(username=verify["username"]).first()
        data = user._asdict()
        del data["password"]
        del data["id"]
        return data


api.add_resource(HealthCheck, "/")
api.add_resource(RegisterUser, "/register")
api.add_resource(UserInfo, "/user-info")
api.add_resource(LogInUser, "/login", methods=["post"])


if __name__ == "__main__":
    Base.metadata.create_all(dbEngine)
    app.run(debug=True)
