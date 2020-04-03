import time

from active.data import login_attempts, opened_drivers
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver


def check_login_timeout(email):
    while time.time() - login_attempts.get(email).timer >= TIME_TO_LOGIN:
        pass
    del login_attempts[email]
    driver_to_close = opened_drivers.get(email)
    close_driver(driver_to_close, email)
