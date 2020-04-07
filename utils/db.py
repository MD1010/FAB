import bcrypt
from pymongo import MongoClient

from consts.db_connection import DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, PLAYERS_COLLECTION, USERS_COLLECTION

cluster = MongoClient(f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0-qs7gn.mongodb.net/{DB_NAME}?retryWrites=true&w=majority', DB_PORT)
fab_db = cluster[DB_NAME]
players_collection = fab_db[PLAYERS_COLLECTION]
users_collection = fab_db[USERS_COLLECTION]


def get_user_from_db_if_exists(email, password):
    user_in_db = users_collection.find_one({"email": email})
    if not user_in_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        return user_in_db
    else:
        return None


def get_user_from_db_by_email(email):
    user_in_db = users_collection.find_one({"email": email})
    return user_in_db


def get_db_user_platform(email):
    user_in_db = users_collection.find_one({"email": email})
    return user_in_db["platform"]


def get_db_username(email):
    user_in_db = users_collection.find_one({"email": email})
    return user_in_db["username"]
