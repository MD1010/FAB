from functools import wraps

import bcrypt
from flask import jsonify, make_response

from consts import server_status_messages, elements
from live_data import active_fabs, user_login_attempts, opened_drivers
from models.fab import Fab


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, player_actions, user):
    return Fab(driver=driver, element_actions=element_actions, player_actions=player_actions, user=user)


def append_new_fab_after_auth_success(fab, user):
    if active_fabs.get(user.email) is None:
        active_fabs[user.email] = fab
    print(active_fabs)


def check_if_web_app_ready(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        if not user_login_attempts.get(email):
            return server_response(msg=server_status_messages.FAILED_AUTH, code=401)
        if not user_login_attempts[email].web_app_ready:
            return server_response(msg=server_status_messages.WEB_APP_IS_STARTING_UP, code=503)
        else:
            return func(email, *args)

    return determine_if_func_should_run


def check_if_fab_opened(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        if email in active_fabs:
            return server_response(msg=server_status_messages.ACTIVE_FAB_EXISTS, code=503)
        else:
            return func(email, *args)

    return determine_if_func_should_run


def verify_driver_opened(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        if email not in opened_drivers:
            return server_response(msg=server_status_messages.DRIVER_OFF, code=503)
        else:
            return func(email, *args)

    return determine_if_func_should_run


def get_coin_balance_from_web_app(element_actions):
    return int(element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))


def server_response(msg, code=200, **kwargs):
    res = jsonify(msg=msg, code=code, **kwargs)
    return make_response(res, code)


# def get_configuration_data(configuration_data):
#     return dict(email=configuration_data["email"], time=configuration_data["time"], list_bought_players=configuration_data["listBoughtPlayers"],
#                 user_decides_buy_prices=configuration_data["userDecidesBuyProces"])
