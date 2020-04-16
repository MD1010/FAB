import datetime
import math

import bcrypt

from consts import elements
from consts.platform import platforms
from consts.prices.prices_consts import MAP_INC_DEC_PRICES
from enums.actions_for_execution import ElementCallback
from live_data import active_fabs
from models.user import User
from utils import db
from utils.helper_functions import get_coin_balance_from_web_app


def update_coin_balance(email, element_actions):
    current_coin_balance = get_coin_balance_from_web_app(element_actions)
    if current_coin_balance:
        active_fabs[email].user.coin_balance = current_coin_balance
        db.users_collection.update({"email": email}, {"$set": {"coin_balance": current_coin_balance}})


def update_db_user_platform(email, element_actions):
    element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    db.users_collection.update({"email": email}, {"$set": {"platform": platforms[platform_icon_class]}})


def update_db_username(email, element_actions):
    element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    username = element_actions.get_element(elements.USER_NAME).text
    db.users_collection.update({"email": email}, {"$set": {"username": username}})


def initialize_user_from_db(email):
    user_from_db = db.users_collection.find_one({"email": email})
    return User(email, user_from_db["password"], user_from_db["cookies"], user_from_db["username"], user_from_db["platform"])


def get_user_from_db_if_exists(email, password):
    user_in_db = db.users_collection.find_one({"email": email})
    if not user_in_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        return user_in_db
    else:
        return None


def get_db_user_platform(email):
    user_in_db = db.users_collection.find_one({"email": email})
    return user_in_db["platform"]


def get_db_username(email):
    user_in_db = db.users_collection.find_one({"email": email})
    return user_in_db["username"]


def update_db_coins_earned(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.users_collection.update({"email": fab.user.email}, {"$inc": {"coins_earned.{}".format(today): int(fab.user.coins_earned)}}, upsert=True)


def update_db_total_runtime(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.users_collection.update({"email": fab.user.email}, {"$inc": {"total_runtime.{}".format(today): fab.user.total_runtime}}, upsert=True)


def update_earned_coins_in_fab(fab, listed_price, bought_price):
    for element in MAP_INC_DEC_PRICES.items():
        values = element[0].split("-")
        if listed_price > float(values[0]) and listed_price < float(values[1]):
            scale = float(element[1])
            break
    deviation = listed_price % scale
    if deviation == scale/2:
        listed_price = listed_price + deviation
    elif deviation > scale/2:
        listed_price = listed_price - deviation + scale
    else:
        listed_price = listed_price - deviation
    fab.user.coins_earned += (math.ceil(listed_price*0.95) - bought_price)
