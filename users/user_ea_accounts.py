from consts import server_status_messages
from models.subscription_plan import SubscriptionPlan
from utils import db
from utils.helper_functions import server_response


def _check_if_account_exists(email):
    return db.users_collection.find_one({"ea_accounts": email})


def add_ea_account_to_user(username, email):
    if _check_if_account_exists(email):
        return server_response(msg=server_status_messages.EA_ACCOUNT_REGISTERED, code=409)
    result = db.users_collection.update({"username": username}, {"$push": {"ea_accounts": email}})
    if result['nModified'] > 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_ADD_SUCCESS, code=201)
    else:
        return server_response(msg=server_status_messages.EA_ACCOUNT_ADD_FAILED, code=500)


def delete_ea_account_from_user(username, email):
    # db.ea_accounts_collection.delete_one({"email": email})
    result = db.users_collection.update({"username": username}, {"$pull": {"ea_accounts": email}})
    if result['nModified'] > 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_SUCCESS, code=200)
    else:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_FAILED, code=500)


def update_user_subscription_plan(username, new_plan_type):
    new_plan = SubscriptionPlan(new_plan_type).__dict__
    result = db.users_collection.update({"username": username}, {"$set": {"plan": new_plan}})
    if result['nModified'] > 0:
        return server_response(msg=server_status_messages.USER_PLAN_UPDATE_SUCCESS, code=200)
    else:
        return server_response(msg=server_status_messages.USER_PLAN_UPDATE_FAILED, code=500)
