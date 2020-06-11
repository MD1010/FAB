import datetime

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

from consts import server_status_messages
from utils import db
from utils.helper_functions import server_response


def log_in_user(username, password):
    user = db.users_collection.find_one({"username": username})
    if not user:
        return server_response(msg=server_status_messages.LOGIN_FAILED, code=401)
    if bcrypt.hashpw(password.encode('utf-8'), user["password"]) == user["password"]:
        token_expires_in_hours = 3
        access_token = create_access_token({'username': username}, expires_delta=datetime.timedelta(hours=token_expires_in_hours))
        refresh_token = create_refresh_token({'username': username}, expires_delta=datetime.timedelta(hours=token_expires_in_hours * 8))
        return server_response(msg=server_status_messages.LOGIN_SUCCESS, code=200, access_token=access_token, refresh_token=refresh_token,
                               expires_in=token_expires_in_hours * 3600)
    else:
        return server_response(msg=server_status_messages.LOGIN_FAILED, code=401)
