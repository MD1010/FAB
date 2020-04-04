import time

from active.data import users_attempted_login, opened_drivers, active_fabs
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver
from utils.helper_functions import get_user_login_attempt


def check_login_timeout(email):
    while time.time() - get_user_login_attempt(email).timer >= TIME_TO_LOGIN:
        pass
    del users_attempted_login[email]
    del active_fabs[email]
    driver_to_close = opened_drivers.get(email)
    close_driver(driver_to_close, email)
