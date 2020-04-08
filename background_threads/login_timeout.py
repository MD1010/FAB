import time

from live_data import user_login_attempts, opened_drivers
from consts.app import TIME_TO_LOGIN
from utils.driver import close_driver


def check_login_timeout(email, app):
    with app.app_context():
        print(user_login_attempts)
        while True:
            if user_login_attempts.get(email) is None: return
            if time.time() - user_login_attempts[email].timer >= TIME_TO_LOGIN or user_login_attempts[email].is_authenticated:
                break
            print(time.time() - user_login_attempts[email].timer)
            time.sleep(1)
            pass

        # time has passed
        login_attempt = user_login_attempts.get(email)
        if login_attempt:
            if not login_attempt.is_authenticated:
                driver_to_close = opened_drivers.get(email)
                close_driver(driver_to_close, email)
