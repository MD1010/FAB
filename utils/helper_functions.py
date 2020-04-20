from functools import wraps

import bcrypt
from flask import jsonify, make_response, request

from consts import server_status_messages, elements
from live_data import active_fabs, ea_account_login_attempts, opened_drivers
from models.fab import Fab


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, item_actions, ea_account):
    return Fab(driver=driver, element_actions=element_actions, item_actions=item_actions, ea_account=ea_account)


def append_new_fab_after_auth_success(fab, ea_account):
    if active_fabs.get(ea_account.email) is None:
        active_fabs[ea_account.email] = fab
    print(active_fabs)


def check_if_web_app_ready(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        json_data = request.get_json()
        user_info = json_data.get('user_info')
        ea_account = user_info['ea_account']
        if not ea_account_login_attempts.get(ea_account):
            return server_response(msg=server_status_messages.WEBAPP_FAILED_AUTH, code=401)
        if not ea_account_login_attempts[ea_account].web_app_ready:
            return server_response(msg=server_status_messages.WEB_APP_IS_STARTING_UP, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run


def check_if_fab_opened(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        json_data = request.get_json()
        user_info = json_data.get('user_info')
        ea_account = user_info['ea_account']
        if ea_account in active_fabs:
            return server_response(msg=server_status_messages.ACTIVE_FAB_EXISTS, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run


def verify_driver_opened(func):
    @wraps(func)
    def determine_if_func_should_run(*args):
        json_data = request.get_json()
        user_info = json_data.get('user_info')
        ea_account = user_info['ea_account']
        if ea_account not in opened_drivers:
            return server_response(msg=server_status_messages.DRIVER_OFF, code=503)
        else:
            return func(*args)

    return determine_if_func_should_run


def get_coin_balance_from_web_app(element_actions):
    if element_actions.get_element(elements.COIN_BALANCE):
        return int(element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    return None


def server_response(msg, code=200, **kwargs):
    res = jsonify(msg=msg, code=code, **kwargs)
    return make_response(res, code)
