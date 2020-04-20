import datetime
from functools import wraps

from flask import request

from consts import server_status_messages
from models.subscription_plan import SubscriptionPlan
from utils import db
from utils.helper_functions import server_response


def update_user_subscription_plan(username, new_plan_type):
    new_plan = SubscriptionPlan(new_plan_type).__dict__
    result = db.users_collection.update({"username": username}, {"$set": {"plan": new_plan}})
    if result['nModified'] > 0:
        return server_response(msg=server_status_messages.USER_PLAN_UPDATE_SUCCESS, code=200)
    else:
        return server_response(msg=server_status_messages.USER_PLAN_UPDATE_FAILED, code=500)


def check_if_subscription_plan_expired(owner):
    user = db.users_collection.find_one({"username": owner})
    if not user:
        return False
    else:
        # if the time now is greater than the expiry time then the account is expired
        if datetime.datetime.now().timestamp() > datetime.datetime.fromisoformat(user['plan']['expiry_date']).timestamp():
            return True
        return False


def check_if_account_limit_exceeded(owner):
    user = db.users_collection.find_one({"username": owner})
    current_user_accounts = len(user["ea_accounts"])
    if current_user_accounts + 1 > user["plan"]["accounts_limit"]:
        return True
    return False
