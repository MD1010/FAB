from utils import db
import bcrypt

from consts import server_status_messages
from utils.server_status import ServerStatus


def check_if_new_user(email):
    existing_user = db.users_collection.find_one({'email': email})
    if existing_user is not None:
        return False
    return True


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def sign_up(email, password):
    is_new_user = check_if_new_user(email)
    if is_new_user:
        hashed_password = hash_password(password)
        cookies = []
        db.users_collection.insert({'email': email, 'password': hashed_password, 'cookies': cookies})
        return ServerStatus(server_status_messages.USER_CREATED,201).jsonify()
    else:
        return ServerStatus(server_status_messages.USER_EXISTS,400).jsonify()
