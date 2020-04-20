from consts import server_status_messages
from utils import db
from utils.helper_functions import hash_password, server_response


def update_user_password(username, new_password):
    new_hashed_password = hash_password(new_password)
    result = db.users_collection.update_one({"username": username}, {"$set": {"password": new_hashed_password}})
    if result.modified_count > 0:
        return server_response(msg=server_status_messages.USER_PASSWORD_UPDATE_SUCCESS, code=200)
    else:
        return server_response(msg=server_status_messages.USER_PASSWORD_UPDATE_FAILED, code=500)


def update_user_username(old_username, new_username):
    users_collection_result = db.users_collection.update_one({"username": old_username}, {"$set": {"username": new_username}})
    if users_collection_result.modified_count == 0:
        return server_response(msg=server_status_messages.USERNAME_UPDATE_FAILED, code=500)
    # update all the accounts that the owner is the old username to the new one
    ea_accounts_collection_result = db.ea_accounts_collection.update_many({"owner":old_username}, {"$set": {"owner": new_username}})
    if ea_accounts_collection_result.modified_count == 0:
        return server_response(msg=server_status_messages.USERNAME_UPDATE_FAILED, code=500)
    return server_response(msg=server_status_messages.USERNAME_UPDATE_SUCESSS, code=200)
