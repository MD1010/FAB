from consts import server_status_messages
from ea_account_info.ea_account_actions import EaAccount
from utils import db
from utils.helper_functions import hash_password


def check_if_new_ea_account(email):
    existing_account = db.ea_accounts_collection.find_one({'email': email})
    if existing_account is not None:
        return False
    return True


def register_new_ea_account_db(email, password, cookies):
    hashed_password = hash_password(password)
    new_account = EaAccount(email, hashed_password, cookies).__dict__
    db.ea_accounts_collection.insert(new_account)
