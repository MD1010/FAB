from functools import wraps
from typing import Dict

from flask import request
from selenium.webdriver.chrome.webdriver import WebDriver
from seleniumwire import webdriver
from urllib3.exceptions import MaxRetryError
from webdriver_manager.chrome import ChromeDriverManager

from consts import app, server_status_messages
from src.web_app.live_logins import login_attempts, running_accounts
from utils.helper_functions import server_response

opened_drivers: Dict[str, 'WebDriver'] = {}


def create_driver_instance(email):
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(app.WEB_APP_URL)
        opened_drivers[email] = driver
        return driver
    except MaxRetryError as e:
        raise e


def close_driver(email):
    driver = opened_drivers.get(email)
    if driver:
        driver.quit()
        if login_attempts.get(email):
            del login_attempts[email]
    running_accounts.remove(email)

def add_running_account(email):
    running_accounts.append(email)

def check_if_driver_is_already_opened(func):
    @wraps(func)
    def determine_if_driver_should_open(*args):
        if request.get_json().get('email') in running_accounts:
            return server_response(msg=server_status_messages.ACCOUNT_ALREADY_RUNNING, code=503)
        return func(*args)

    return determine_if_driver_should_open
