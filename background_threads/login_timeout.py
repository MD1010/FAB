import time

from active.data import user_login_attempts, opened_drivers, active_fabs
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver




def check_login_timeout(email):
    print(user_login_attempts)
    while time.time() - user_login_attempts[email].timer <= TIME_TO_LOGIN and not user_login_attempts[email].is_authenticated:
        print(time.time() - user_login_attempts[email].timer)
        time.sleep(1)
        pass

    # time has passed
    if not user_login_attempts[email].is_authenticated:

        driver_to_close = opened_drivers.get(email)
        close_driver(driver_to_close, email)

