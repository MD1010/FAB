import datetime
from functools import wraps

import bcrypt
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from consts import server_status_messages
from utils import db
from utils.helper_functions import server_response
from utils.tokens import access_tokens, refresh_tokens


def check_if_user_was_authenticated(func):
    @wraps(func)
    def determine_if_func_should_run(**kwargs):
        token = request.headers.get('Authorization').split()[1]
        username = get_jwt_identity()
        if token not in access_tokens.get(username) and token not in refresh_tokens.get(username):
            return server_response(msg=server_status_messages.AUTH_FAILED, code=401)
        return func(username, **kwargs)

    return determine_if_func_should_run


def log_in_user(username, password):
    user = db.users_collection.find_one({"username": username})
    if not user:
        return server_response(msg=server_status_messages.LOGIN_FAILED, code=401)
    if bcrypt.hashpw(password.encode('utf-8'), user["password"]) == user["password"]:
        access_token = create_access_token(username, expires_delta=datetime.timedelta(seconds=5))
        refresh_token = create_refresh_token(username, expires_delta=datetime.timedelta(days=1))
        access_tokens[username] = (access_tokens.get(username) or []) + [access_token]
        refresh_tokens[username] = (refresh_tokens.get(username) or []) + [refresh_token]
        return server_response(msg=server_status_messages.LOGIN_SUCCESS, access_token=access_token, refresh_token=refresh_token)
    else:
        return server_response(msg=server_status_messages.LOGIN_FAILED, code=401)
