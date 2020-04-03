import time

from active.data import active_login_sessions, opened_drivers
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver


def check_login_timeout(email):
    while time.time() - active_login_sessions.get(email).timer >= TIME_TO_LOGIN:
        pass
    del active_login_sessions[email]
    driver_to_close = opened_drivers.get(email)
    close_driver(driver_to_close, email)
