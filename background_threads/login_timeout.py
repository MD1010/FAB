import time

from active.data import users_attempted_login, opened_drivers, active_fabs
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver
from utils.helper_functions import get_user_login_attempt



def check_login_timeout(email):
    print(users_attempted_login)
    while time.time() - get_user_login_attempt(email).timer <= TIME_TO_LOGIN and not get_user_login_attempt(email).is_authenticated:
        print(time.time() - get_user_login_attempt(email).timer)
        time.sleep(1)
        pass

    # time has passed
    if get_user_login_attempt(email).is_authenticated == False:
        del users_attempted_login[email]
        driver_to_close = opened_drivers.get(email)
        close_driver(driver_to_close, email)

