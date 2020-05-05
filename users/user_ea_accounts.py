from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity

from consts import server_status_messages
from users.subscription_plan import check_if_account_limit_exceeded
from utils import db
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
        #first login
        if user_account is None:
            return func(*args)
        account_owner = user_account['owner']
        if account_owner != owner:
            return server_response(msg=server_status_messages.EA_ACCOUNT_BELONGS_TO_ANOTHER_USER, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run
