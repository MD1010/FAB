import threading
import time

from live_data import ea_account_login_attempts, opened_drivers
from consts.app import TIME_TO_LOGIN
from utils.driver_functions import close_driver


def check_login_timeout(email, app):
    with app.app_context():
        while True:
            if ea_account_login_attempts.get(email) is None: return
            if time.time() - ea_account_login_attempts[email].timer >= TIME_TO_LOGIN or ea_account_login_attempts[email].is_authenticated:
                break
            print(time.time() - ea_account_login_attempts[email].timer)
            time.sleep(1)
            pass

        # time has passed
        login_attempt = ea_account_login_attempts.get(email)
        if login_attempt:
            if not login_attempt.is_authenticated:
                driver_to_close = opened_drivers.get(email)
                close_driver(driver_to_close, email)


def open_login_timeout_thread(func, email,app):
    new_thread = threading.Thread(target=func, args=(email,app))
    new_thread.start()

