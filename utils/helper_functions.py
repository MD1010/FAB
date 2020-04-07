from functools import wraps

import bcrypt
from flask import jsonify

from active.data import active_fabs, user_login_attempts, opened_drivers
from consts import server_status_messages
from fab import Fab


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, player_actions, user):
    return Fab(driver=driver, element_actions=element_actions, player_actions=player_actions, user=user)


def append_new_fab_after_auth_success(fab, user):
    if active_fabs.get(user["email"]) is None:
        active_fabs[user["email"]] = fab


def check_if_web_app_ready(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        if not user_login_attempts.get(email):
            return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
        if not user_login_attempts[email].web_app_ready:
            return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
        else:
            return func(email, *args)

    return determine_if_func_should_run

def check_if_fab_opened(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        if email in active_fabs:
            return jsonify(msg=server_status_messages.ACTIVE_FAB_EXISTS, code=503)
        else:
            return func(email, *args)

    return determine_if_func_should_run

def verify_driver_opened(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        if email not in opened_drivers:
            return jsonify(msg=server_status_messages.DRIVER_OFF, code=503)
        else:
            return func(email, *args)

    return determine_if_func_should_run
