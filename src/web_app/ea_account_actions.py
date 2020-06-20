import datetime
import math
from functools import wraps

import bcrypt
from flask import request
from flask_jwt_extended import get_jwt_identity

from consts import MAP_INC_DEC_PRICES
from consts import server_status_messages
from models import EaAccount
from src.users.subscription_plan import check_if_account_limit_exceeded
from utils import db
from utils.helper_functions import hash_password
from utils.helper_functions import server_response


def _check_if_account_exists(email):
    return db.users_collection.find_one({"ea_accounts": email})


def add_ea_account_to_user(username, email):
    if _check_if_account_exists(email):
        return server_response(msg=server_status_messages.EA_ACCOUNT_REGISTERED, code=409)
    if check_if_account_limit_exceeded(username):
        return server_response(msg=server_status_messages.ACCOUNT_LIMIT_EXCEEDED, code=503)
    result = db.users_collection.update_one({"username": username}, {"$push": {"ea_accounts": email}})
    if result.modified_count > 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_ADD_SUCCESS, code=201)
    else:
        return server_response(msg=server_status_messages.EA_ACCOUNT_ADD_FAILED, code=500)


def delete_ea_account_from_user(username, email):
    ea_accounts_result = db.ea_accounts_collection.delete_one({"owner": username, "email": email})
    if ea_accounts_result.deleted_count == 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_FAILED, code=500)
    users_result = db.users_collection.update_one({"username": username}, {"$pull": {"ea_accounts": email}})
    if users_result.modified_count > 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_SUCCESS, code=200)
    else:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_FAILED, code=500)


def check_if_user_owns_ea_account(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        owner = get_jwt_identity()['username']
        json_data = request.get_json()
        email = json_data.get('email')
        # check if owner or username fields exist
        user_account = db.ea_accounts_collection.find_one({"email": email})
        # first login
        if user_account is None:
            return func(*args)
        account_owner = user_account['owner']
        if account_owner != owner:
            return server_response(msg=server_status_messages.EA_ACCOUNT_BELONGS_TO_ANOTHER_USER, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run


def initialize_ea_account_from_db(owner, email):
    ea_account_from_db = db.ea_accounts_collection.find_one({"email": email})
    return EaAccount(owner, email, ea_account_from_db["password"], ea_account_from_db["cookies"], ea_account_from_db["username"], ea_account_from_db["platform"])


def get_ea_account_if_exists(email, password):
    ea_account_from_db = db.ea_accounts_collection.find_one({"email": email})
    if not ea_account_from_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), ea_account_from_db["password"]) == ea_account_from_db["password"]:
        return ea_account_from_db
    else:
        return None


def get_ea_account_platform(email):
    ea_account = db.ea_accounts_collection.find_one({"email": email})
    return ea_account["platform"]


def get_ea_account_username(email):
    ea_account = db.ea_accounts_collection.find_one({"email": email})
    return ea_account["username"]


def update_ea_account_coins_earned(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.ea_accounts_collection.update({"email": fab.ea_account.email}, {"$inc": {"coins_earned.{}".format(today): int(fab.ea_account.coins_earned)}}, upsert=True)


def update_ea_account_total_runtime(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.ea_accounts_collection.update({"email": fab.ea_account.email}, {"$inc": {"total_runtime.{}".format(today): fab.ea_account.total_runtime}}, upsert=True)


def check_if_new_ea_account(email):
    existing_account = db.ea_accounts_collection.find_one({'email': email})
    if existing_account is not None:
        return False
    return True


def register_new_ea_account(owner, email, password, cookies):
    hashed_password = hash_password(password)
    new_account = EaAccount(owner, email, hashed_password, cookies).__dict__
    return db.ea_accounts_collection.insert(new_account)


def update_earned_coins_in_fab(fab, listed_price, bought_price):
    for element in MAP_INC_DEC_PRICES.items():
        values = element[0].split("-")
        if float(values[0]) < listed_price < float(values[1]):
            scale = float(element[1])
            break
    deviation = listed_price % scale
    if deviation == scale / 2:
        listed_price = listed_price + deviation
    elif deviation > scale / 2:
        listed_price = listed_price - deviation + scale
    else:
        listed_price = listed_price - deviation
    fab.ea_account.coins_earned += (math.ceil(listed_price * 0.95) - bought_price)
