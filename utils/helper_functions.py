from functools import wraps

import bcrypt
from flask import jsonify

from active.data import active_fabs, opened_drivers
from consts import server_status_messages
from fab import Fab


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, player_actions, user):
    return Fab(driver=driver, element_actions=element_actions, player_actions=player_actions, user=user)


def append_new_fab_after_auth_success(fab, user):
    active_fabs[user["email"]] = fab


def check_auth_status(func):
    @wraps(func)
    def determine_if_func_should_run(email, *args):
        current_fab = active_fabs.get(email)
        if current_fab is None:
            return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
        else:
            return func(email, *args)

    return determine_if_func_should_run
