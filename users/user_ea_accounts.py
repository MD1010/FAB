from consts import server_status_messages
from models.subscription_plan import SubscriptionPlan
from utils import db
from utils.helper_functions import server_response


def _check_if_account_exists(email):
    return db.users_collection.find_one({"ea_accounts": email})


def add_ea_account_to_user(username, email):
    if _check_if_account_exists(email):
        return server_response(msg=server_status_messages.EA_ACCOUNT_REGISTERED, code=409)
    db.users_collection.update({"username": username}, {"$push": {"ea_accounts": email}})
    return server_response(msg=server_status_messages.EA_ACCOUNT_ADDED, code=201)


def delete_ea_account_from_user(username, email):
    db.ea_accounts_collection.delete_one({"email": email})
    db.users_collection.update({"username": username}, {"$pull": {"ea_accounts": email}})
    return server_response(msg=server_status_messages.EA_ACCOUNT_DELETED, code=200)


def update_user_subscription_plan(username, new_plan_type):
    new_plan = SubscriptionPlan(new_plan_type).__dict__
    db.users_collection.update({"username": username}, {"$set":{"plan": new_plan}})
    return server_response(msg=server_status_messages.USER_PLAN_UPDATED, code=200)
