import time
from enum import Enum

from flask import jsonify
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from active.data import opened_drivers, active_fabs, users_attempted_login
from consts import app, server_status_messages, elements
from consts.app import AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION
from utils.fab_loop import start_fab

from pyvirtualdisplay import Display


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


def restart_driver_when_crashed(fab, requested_players):
    return start_fab(fab.time_left_to_run, requested_players)


def close_driver(driver, email):
    if driver is not None:
        driver.quit()
        del users_attempted_login[email]
        del opened_drivers[email]


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


def check_if_web_app_is_available(driver):
    getting_started = driver.element_actions.get_element(elements.GETTING_STARTED)
    logged_on_console = driver.element_actions.get_element(elements.LOGGED_ON_CONSOLE)
    login_captcha = driver.element_actions.get_element(elements.LOGIN_CAPTHA)
    login_popup = driver.element_actions.get_element(elements.LOGIN_POPUP)
    if getting_started or logged_on_console or login_captcha or login_popup:
        return False
    return True
