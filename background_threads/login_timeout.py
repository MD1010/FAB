import time

from active.data import users_attempted_login, opened_drivers, active_fabs
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver




def check_login_timeout(email):
    print(users_attempted_login)
    while time.time() - users_attempted_login[email].timer <= TIME_TO_LOGIN and not users_attempted_login[email].is_authenticated:
        print(time.time() - users_attempted_login[email].timer)
        time.sleep(1)
        pass

    # time has passed
    if not users_attempted_login[email].is_authenticated:
        del users_attempted_login[email]
        driver_to_close = opened_drivers.get(email)
        close_driver(driver_to_close, email)

