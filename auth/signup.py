from flask import jsonify

from consts import server_status_messages
from user_info.user import User
from utils import db
from utils.helper_functions import hash_password


def check_if_new_user(email):
    existing_user = db.users_collection.find_one({'email': email})
    if existing_user is not None:
        return False
    return True


def sign_up(email, password):
    is_new_user = check_if_new_user(email)
    if is_new_user:
        hashed_password = hash_password(password)
        db.users_collection.insert(User(email, hashed_password).__dict__)
        return jsonify(msg=server_status_messages.USER_CREATED, code=201)
    else:
        return jsonify(msg=server_status_messages.USER_EXISTS, code=409)
