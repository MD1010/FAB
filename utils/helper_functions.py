from functools import wraps

import bcrypt
from flask import jsonify, make_response, request

from consts import server_status_messages, elements
from live_data import active_fabs, user_login_attempts, opened_drivers
from models.fab import Fab


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, item_actions, user):
    return Fab(driver=driver, element_actions=element_actions, item_actions=item_actions, user=user)


def append_new_fab_after_auth_success(fab, user):
    if active_fabs.get(user.email) is None:
        active_fabs[user.email] = fab
    print(active_fabs)


def check_if_web_app_ready(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        jsonData = request.get_json()
        user_email = jsonData.get('user')
        if not user_login_attempts.get(user_email):
            return server_response(msg=server_status_messages.FAILED_AUTH, code=401)
        if not user_login_attempts[user_email].web_app_ready:
            return server_response(msg=server_status_messages.WEB_APP_IS_STARTING_UP, code=503)
        else:
            return func(*args)
    return determine_if_func_should_run


def check_if_fab_opened(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        jsonData = request.get_json()
        user_email = jsonData.get('user')
        if user_email in active_fabs:
            return server_response(msg=server_status_messages.ACTIVE_FAB_EXISTS, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run


def verify_driver_opened(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        jsonData = request.get_json()
        user_email = jsonData.get('user')
        if user_email not in opened_drivers:
            return server_response(msg=server_status_messages.DRIVER_OFF, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run


def get_coin_balance_from_web_app(element_actions):
    return int(element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))


def server_response(msg, code=200, **kwargs):
    res = jsonify(msg=msg, code=code, **kwargs)
    return make_response(res, code)


