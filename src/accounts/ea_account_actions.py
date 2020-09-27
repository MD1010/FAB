import datetime

from consts import server_status_messages
from models import EaAccount
from utils import db
from utils.helper_functions import hash_password
from utils.helper_functions import server_response


def _check_if_account_exists(email):
    return db.users_collection.find_one({"ea_accounts": email})


def delete_ea_account_from_user(username, email):
    ea_accounts_result = db.ea_accounts_collection.delete_one({"owner": username, "email": email})
    if ea_accounts_result.deleted_count == 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_FAILED, code=500)
    users_result = db.users_collection.update_one({"username": username}, {"$pull": {"ea_accounts": email}})
    if users_result.modified_count > 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_SUCCESS, code=200)
    else:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_FAILED, code=500)


def update_ea_account_coins_earned(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.ea_accounts_collection.update({"email": fab.ea_account.email}, {"$inc": {"coins_earned.{}".format(today): int(fab.ea_account.coins_earned)}}, upsert=True)


def update_ea_account_total_runtime(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.ea_accounts_collection.update({"email": fab.ea_account.email}, {"$inc": {"total_runtime.{}".format(today): fab.ea_account.total_runtime}}, upsert=True)


def check_account_if_exists(email):
    existing_account = db.ea_accounts_collection.find_one({'email': email})
    return existing_account


def register_new_ea_account(owner, email, password, cookies):
    hashed_password = hash_password(password)
    new_account = EaAccount(owner, email, hashed_password, cookies).__dict__
    return db.ea_accounts_collection.insert(new_account)
