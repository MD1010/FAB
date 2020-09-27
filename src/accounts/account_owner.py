from functools import wraps

from flask import request
from flask_jwt_extended import get_jwt_identity

from consts import server_status_messages
from utils import db
from utils.helper_functions import server_response


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
            return func(owner)
        account_owner = user_account.get('owner')
        if account_owner != owner:
            return server_response(msg=server_status_messages.EA_ACCOUNT_BELONGS_TO_ANOTHER_USER, code=503)
        else:
            print("OWNER!!"+account_owner)
            return func(account_owner)

    return determine_if_func_should_run