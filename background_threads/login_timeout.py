import time

from active.data import users_attempted_login, opened_drivers
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver


def check_login_timeout(email):
    while time.time() - users_attempted_login.get(email).timer >= TIME_TO_LOGIN:
        pass
    del users_attempted_login[email]
    driver_to_close = opened_drivers.get(email)
    close_driver(driver_to_close, email)
