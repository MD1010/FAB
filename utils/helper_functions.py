import bcrypt
from flask import jsonify, make_response


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def server_response(code=200, **kwargs):
    res = jsonify(**kwargs)
    return make_response(res, code)


def destructor(**kwargs):
    return kwargs.values()
