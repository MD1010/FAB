from user_info.user import User
from utils import db
from utils.helper_functions import hash_password


def check_if_new_user(email):
    existing_user = db.users_collection.find_one({'email': email})
    if existing_user is not None:
        return False
    return True


def register_new_user_to_db(email, password, cookies):
    hashed_password = hash_password(password)
    new_user = User(email, hashed_password, cookies).__dict__
    db.users_collection.insert(new_user)
