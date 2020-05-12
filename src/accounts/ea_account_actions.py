import datetime
import math

import bcrypt

from consts.prices_consts import MAP_INC_DEC_PRICES
from models.ea_account import EaAccount
from utils import db
from utils.helper_functions import hash_password


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
