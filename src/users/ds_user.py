import bcrypt

from models import User
from utils import db
from utils.exceptions import UserNotFound
from utils.helper_functions import hash_password


def get_user_from_db_if_exists(email, password):
    user_in_db = db.users_collection.find_one({"email": email})
    if not user_in_db:
        raise UserNotFound()
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        return user_in_db

# def register_new_user_to_db(email, password, cookies):
#     hashed_password = hash_password(password)
#     new_user = User(email, hashed_password, cookies).__dict__
#     db.users_collection.insert(new_user)
