import time
from enum import Enum

import psutil
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from consts import app, server_status_messages, elements
from selenium import webdriver

from consts.app import CHROME_DRIVER_PROCESS_NAME, AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION
from utils.helper_functions import jsonify
from utils.server_status import ServerStatus


class DriverState(Enum):
    ON = "on"
    OFF = "off"


class Driver:
    def __init__(self, driver):
        self.driver = driver


def initialize_driver(self):
    try:
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(app.WEB_APP_URL)
        self.driver_state = DriverState.ON
    except:
        raise WebDriverException()

def initialize_time_left(self,time_to_run_in_sec):
    self.time_left_to_run = time_to_run_in_sec

def restart_driver_when_crashed(self,requested_players):
    # close_driver(self)
    # self.start_login(self.connected_user_details["email"], self.connected_user_details["password"])
    self.start_loop(self.time_left_to_run, requested_players)

def close_driver(self):
    if self.driver is not None:
        self.driver.quit()
        for proc in psutil.process_iter():
            if proc.name() == CHROME_DRIVER_PROCESS_NAME:
                proc.kill()
        self.driver_state = DriverState.OFF
        self.set_auth_status = False
        return jsonify(ServerStatus(server_status_messages.FAB_DRIVER_CLOSE_SUCCESS, 200))
    else:
        return jsonify(ServerStatus(server_status_messages.FAB_DRIVER_CLOSE_FAIL, 503))

def evaluate_driver_operation_time(self,start_time,time_to_run_in_sec,num_of_tries):
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



