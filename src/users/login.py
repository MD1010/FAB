import datetime
from functools import wraps

import bcrypt
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from consts import server_status_messages
from utils import db
from utils.helper_functions import server_response
from utils.tokens import access_tokens, refresh_tokens


def check_if_user_authenticated(func):
    @wraps(func)
    def determine_if_func_should_run():
        token = request.headers.get('Authorization').split()[1]
        username = get_jwt_identity()['username']
        if access_tokens.get(username) != token and refresh_tokens.get(username) != token:
            return server_response(status=server_status_messages.AUTH_FAILED, code=401)
        return func(username)

    return determine_if_func_should_run


def log_in_user(username, password):
    user = db.users_collection.find_one({"username": username})
    if not user:
        return server_response(msg=server_status_messages.LOGIN_FAILED, code=401)
    if bcrypt.hashpw(password.encode('utf-8'), user["password"]) == user["password"]:
        token_expires_in_hours = 3
        access_token = create_access_token({'username': username}, expires_delta=datetime.timedelta(hours=token_expires_in_hours))
        refresh_token = create_refresh_token({'username': username}, expires_delta=datetime.timedelta(hours=token_expires_in_hours * 8))
        access_tokens[username] = access_token
        refresh_tokens[username] = refresh_token
        return server_response(msg=server_status_messages.LOGIN_SUCCESS, code=200, access_token=access_token, refresh_token=refresh_token,
                               expires_in=token_expires_in_hours * 3600)
    else:
        return server_response(msg=server_status_messages.LOGIN_FAILED, code=401)
