import datetime

from consts import server_status_messages
from models import EaAccount
from utils import db
from utils.helper_functions import server_response, encrypt_password

from models import EaAccountStatus


def _check_if_account_exists(email):
    return db.users_collection.find_one({"ea_accounts": email})

def check_account_if_exists(email):
    existing_account = db.ea_accounts_collection.find_one({'email': email})
    return existing_account

def get_owner_accounts(owner):
    accounts = []
    collection = db.ea_accounts_collection.find({"owner": owner}, {'_id': 0, 'cookies': 0, 'password': 0, "passKey": 0})

    for account in collection:
        accounts.append(account)

    return server_response(accounts=accounts)

def add_new_ea_account(owner, email):
    if check_account_if_exists(email):
        return server_response(msg=server_status_messages.EA_ACCOUNT_REGISTERED, code=400)
    new_account = EaAccount(owner, email).__dict__
    try:
        db.ea_accounts_collection.insert_one(new_account)
        return server_response(owner=owner, msg=server_status_messages.EA_ACCOUNT_ADD_SUCCESS, code=201)
    except:
        return server_response(msg=server_status_messages.EA_ACCOUNT_ADD_FAILED, code=500)

def delete_ea_account_from_user(owner, email):
    ea_accounts_result = db.ea_accounts_collection.delete_one({"owner": owner, "email": email})
    if ea_accounts_result.deleted_count == 0:
        return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_FAILED, code=400)
    return server_response(msg=server_status_messages.EA_ACCOUNT_DELETE_SUCCESS, code=200)

def update_ea_account_logged_details(email, password, cookies):
    encrypted_password, key = encrypt_password(password)
    db.ea_accounts_collection.update_one({"email": email}, { "$set": { "password": encrypted_password, "cookies": cookies, "passKey": key }}, upsert=True)

def update_ea_account_status(email, status):
    res = db.ea_accounts_collection.update_one({"email": email}, { "$set": { "status": status.value}}, upsert=True)
    if res.modified_count > 0 and status == EaAccountStatus.RUNNING:
        return server_response(code=200, msg=server_status_messages.EA_ACCOUNT_LOGIN_SUCCESS)
    return server_response(code=200, msg=server_status_messages.EA_ACCOUNT_RUNNING_SUCCESS)

def update_ea_account_coins_earned(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.ea_accounts_collection.update({"email": fab.ea_account.email}, {"$inc": {"coins_earned.{}".format(today): int(fab.ea_account.coins_earned)}}, upsert=True)

def update_ea_account_total_runtime(fab):
    today = str(datetime.datetime.today().strftime('%d-%m-%Y'))
    db.ea_accounts_collection.update({"email": fab.ea_account.email}, {"$inc": {"total_runtime.{}".format(today): fab.ea_account.total_runtime}}, upsert=True)

def add_search_filter_to_account(account, search_filter):
    res = db.ea_accounts_collection.update_one({'email': account}, {"$push": {"search_filters": search_filter}})
    if res.modified_count > 0:
        return server_response(code=201, msg=server_status_messages.NEW_SEARCH_FILTER_ADD_SUCCESS)
    return server_response(code=503, msg=server_status_messages.NEW_SEARCH_FILTER_ADD_FAIL)

def remove_search_filter_to_account(account, filter_id):
    res = db.ea_accounts_collection.update_one({'email': account}, {"$pull": {"search_filters": {"id": filter_id}}})
    if res.modified_count > 0:
        return server_response(code=200, msg=server_status_messages.SEARCH_FILTER_REMOVE_SUCCESS)
    return server_response(code=503, msg=server_status_messages.SEARCH_FILTER_REMOVE_FAIL)

def set_selected_filter(account, filter_id):
    found_filter = db.ea_accounts_collection.find_one({'email': account}, {"search_filters": {"$elemMatch": {"id": filter_id}}})['search_filters'][0]
    if not found_filter:
        return server_response(code=503, msg=server_status_messages.MAIN_SEARCH_FILTER_SET_FAIL)
    res = db.ea_accounts_collection.update_one({'email': account}, {"$set": {"selected_search_filter": found_filter['id']}})
    if res.modified_count > 0:
        return server_response(code=200, msg=server_status_messages.MAIN_SEARCH_FILTER_SET_SUCESS)
    return server_response(code=503, msg=server_status_messages.MAIN_SEARCH_FILTER_SET_FAIL)
