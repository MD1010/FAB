import json

import bcrypt

from active.data import active_fabs
from fab import Fab
from utils import db


def saveToCookiesFile(obj, name):
    with open(name, 'w') as f:
        f.write(json.dumps(obj))


def loadCookiesFile(name):
    with open(name, 'r') as f:
        return json.load(f)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, player_actions, user):
    fab = Fab(driver=driver, element_actions=element_actions, player_actions=player_actions, user=user)
    active_fabs[user.email] = fab
    return fab


def get_user_from_db_if_exists(email, password):
    user_in_db = db.users_collection.find_one({"email": email})
    if not user_in_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        return user_in_db
    else:
        return None

def get_user_platform(email):
    user_in_db = db.users_collection.find_one({"email": email})
    return user_in_db["platform"]

def get_user_name(email):
    user_in_db = db.users_collection.find_one({"email": email})
    return user_in_db["user_name"]
