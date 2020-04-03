import time
from enum import Enum

from flask import jsonify
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from active.data import opened_drivers
from consts import app, server_status_messages, elements
from consts.app import AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION


class DriverState(Enum):
    ON = "on"
    OFF = "off"


class Driver:
    def __init__(self, driver):
        self.driver = driver



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


def initialize_time_left(self, time_to_run_in_sec):
    self.time_left_to_run = time_to_run_in_sec


def restart_driver_when_crashed(self, requested_players):
    self.start_fab(self.time_left_to_run, requested_players)


def close_driver(self):
    if self.driver is not None:
        self.driver.quit()
        self.driver = None
        self.driver_state = DriverState.OFF
        return jsonify(msg=server_status_messages.FAB_DRIVER_CLOSE_SUCCESS, code=200)
    else:
        return jsonify(msg=server_status_messages.FAB_DRIVER_CLOSE_FAIL, code=503)


def evaluate_driver_operation_time(self, start_time, time_to_run_in_sec, num_of_tries):
    curr_time = time.time()
    elapsed_time = curr_time - start_time
    if elapsed_time > time_to_run_in_sec:
        self.time_left_to_run = 0
        return False
    self.time_left_to_run = time_to_run_in_sec - elapsed_time
    num_of_tries += 1
    if num_of_tries % AMOUNT_OF_SEARCHES_BEFORE_SLEEP == 0:
        time.sleep(SLEEP_MID_OPERATION_DURATION)
    time.sleep(1)
    return num_of_tries


def check_if_web_app_is_available(self):
    getting_started = self.element_actions.get_element(elements.GETTING_STARTED)
    logged_on_console = self.element_actions.get_element(elements.LOGGED_ON_CONSOLE)
    login_captcha = self.element_actions.get_element(elements.LOGIN_CAPTHA)
    login_popup = self.element_actions.get_element(elements.LOGIN_POPUP)
    if getting_started or logged_on_console or login_captcha or login_popup:
        return False
    return True
