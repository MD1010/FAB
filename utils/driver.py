import time
from enum import Enum

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from active.data import opened_drivers, user_login_attempts, active_fabs
from consts import app, server_status_messages
from consts.app import AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION
from utils.helper_functions import server_response


class DriverState(Enum):
    ON = "on"
    OFF = "off"


class Driver:
    def __init__(self, driver):
        self.driver = driver


def get_or_create_driver_instance(email):
    if email in opened_drivers:
        return opened_drivers.get(email)
    else:
        return initialize_driver(email)


def initialize_driver(email):
    try:

        driver = webdriver.Chrome(ChromeDriverManager().install())
        opened_drivers[email] = driver
        print(driver.service.process.pid)
        driver.get(app.WEB_APP_URL)
        return driver
        # new_driver.driver_state = DriverState.ON
    except:
        raise WebDriverException()


def initialize_time_left(fab, time_to_run_in_sec):
    fab.time_left_to_run = time_to_run_in_sec


def close_driver(driver, email):
    if driver is not None:
        driver.quit()
        login_attempt = user_login_attempts.get(email)
        current_driver = opened_drivers.get(email)
        fab = active_fabs.get(email)
        if login_attempt:
            del user_login_attempts[email]
        if current_driver:
            del opened_drivers[email]
        if fab:
            del active_fabs[email]
        return server_response(msg=server_status_messages.FAB_DRIVER_CLOSE_SUCCESS, code=200)
    return server_response(msg=server_status_messages.FAB_DRIVER_CLOSE_FAIL, code=503)


def evaluate_driver_operation_time(fab, start_time, time_to_run_in_sec, num_of_tries):
    curr_time = time.time()
    elapsed_time = curr_time - start_time
    if elapsed_time > time_to_run_in_sec:
        fab.time_left_to_run = 0
        return False
    fab.time_left_to_run = time_to_run_in_sec - elapsed_time
    num_of_tries += 1
    if num_of_tries % AMOUNT_OF_SEARCHES_BEFORE_SLEEP == 0:
        time.sleep(SLEEP_MID_OPERATION_DURATION)
    time.sleep(1)
    return num_of_tries
