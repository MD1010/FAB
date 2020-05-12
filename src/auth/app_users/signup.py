from consts import server_status_messages
from consts.subscription_plans import TRIAL
from models.subscription_plan import SubscriptionPlan
from models.user import User
from utils import db
from utils.helper_functions import hash_password, server_response


def _check_if_new_user(username):
    existing_user = db.users_collection.find_one({'username': username})
    if existing_user is None:
        return True
    return False


def create_new_user(username, password):
    is_new_user = _check_if_new_user(username)
    if is_new_user:
        hashed_password = hash_password(password)
        user_basic_subscription_plan = SubscriptionPlan(TRIAL).__dict__
        new_user = User(username, hashed_password, user_basic_subscription_plan).__dict__
        result = db.users_collection.insert(new_user)
        if result:
            return server_response(msg=server_status_messages.USER_CREATE_SUCCESS, code=201)
        else:
            return server_response(msg=server_status_messages.USER_CREATE_FAILED, code=500)
    else:
        return server_response(msg=server_status_messages.USER_EXISTS, code=409)
