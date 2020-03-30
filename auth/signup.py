from bson.objectid import ObjectId

from consts import server_status_messages, app
from user_info.user import User
from utils import db
from utils.helper_functions import jsonify, hash_password
from utils.server_status import ServerStatus


def check_if_new_user(email):
    existing_user = db.users_collection.find_one({'email': email})
    if existing_user is not None:
        return False
    return True


def sign_up(email, password):
    # cookies = loadCookiesFile(app.COOKIES_FILE_NAME)
    # db.users_collection.update({"_id": ObjectId("5e823f9f807a0195913873b5")}, {"$set": {"cookies": cookies}})
    is_new_user = check_if_new_user(email)
    if is_new_user:
        hashed_password = hash_password(password)
        db.users_collection.insert(User(email,hashed_password).__dict__)
        return jsonify(ServerStatus(server_status_messages.USER_CREATED, 201))
    else:
        return jsonify(ServerStatus(server_status_messages.USER_EXISTS, 400))
