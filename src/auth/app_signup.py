from consts import server_status_messages
from models import User
from utils import db
from utils.helper_functions import hash_password, server_response


def _check_if_new_user(username):
    existing_user = db.users_collection.find_one({'username': username})
    if existing_user is None:
        return True
    return False


def create_new_user(username, password):
    is_new_user = _check_if_new_user(username)
    if is_new_user:
        hashed_password = hash_password(password)
        new_user = User(username, hashed_password).__dict__
        result = db.users_collection.insert(new_user)
        if result:
            return server_response(msg=server_status_messages.USER_CREATE_SUCCESS, code=201)
        else:
            return server_response(msg=server_status_messages.USER_CREATE_FAILED, code=500)
    else:
        return server_response(msg=server_status_messages.USER_EXISTS, code=409)
