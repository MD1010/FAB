import bcrypt
from flask import jsonify, make_response
from flask_jwt_extended import get_jwt_identity, create_access_token


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def server_response(msg, code=200, **kwargs):
    res = jsonify(msg=msg, code=code, **kwargs)
    return make_response(res, code)


def refresh_access_token():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
