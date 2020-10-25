from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity
from consts import server_status_messages
from utils import db
from utils.helper_functions import server_response, decrypt_password


def check_if_user_owns_ea_account(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        owner = get_jwt_identity()
        json_data = request.get_json()
        email = json_data.get('email')
        # check if owner or username fields exist
        user_account = db.ea_accounts_collection.find_one({"email": email})
        # first login
        if user_account is None:
            return func(owner)
        account_owner = user_account.get('owner')
        if account_owner != owner:
            return server_response(msg=server_status_messages.EA_ACCOUNT_BELONGS_TO_ANOTHER_USER, code=503)
        else:

            return func(owner)

    return determine_if_func_should_run

def check_if_user_first_login(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        json_data = request.get_json()
        email = json_data.get('email')
        # check if owner or username fields exist
        user_account = db.ea_accounts_collection.find_one({"email": email})
        # first login
        if not user_account["password"]:
            return server_response(msg="should login first", code=200)

        password = decrypt_password(user_account["password"])
        return func(user_account.get('owner'), email, password)

    return determine_if_func_should_run