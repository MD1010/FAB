import datetime

from flask import jsonify
from flask_jwt_extended import create_access_token
from selenium.common.exceptions import TimeoutException

from active.data import active_fabs, user_login_attempts
from auth.auth_status import set_auth_status
from auth.selenium_login import SeleniumLogin
from auth.signup import register_new_user_to_db
from consts import server_status_messages, app
from elements.elements_manager import ElementActions
from players.players_actions import PlayerActions
from user_info.user import update_db_user_platform, update_db_username, User
from utils.db import get_user_from_db_if_exists
from utils.driver import get_or_create_driver_instance
from utils.helper_functions import create_new_fab, append_new_fab_after_auth_success


# def check_auth_status(func):
#     @wraps(func)
#     def determine_if_func_should_run(self, *args):
#         if not self.is_authenticated:
#             return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
#         return func(self, *args)
#
#     return determine_if_func_should_run


def start_login(email, password):
    # if user exists in db then he must have already logged in before and he has cookies
    existing_user = get_user_from_db_if_exists(email, password)

    try:
        driver = get_or_create_driver_instance(email)
        element_actions = ElementActions(driver)
        player_actions = PlayerActions(element_actions)
        selenium_login = SeleniumLogin(driver, element_actions)
        new_user = User(email)

        if existing_user:
            first_time_login = False
            if not selenium_login.login_with_cookies(password, email, existing_user["cookies"]):
                return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
            active_fab = create_new_fab(driver, element_actions, player_actions, new_user)

        # cookies file was not found - log in the first time
        else:
            first_time_login = True
            if not selenium_login.login_first_time(email, password):
                return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
            active_fab = create_new_fab(driver, element_actions, player_actions, new_user)

            status_code_result = wait_for_status_code_loop(email)
            if not status_code_result:
                return jsonify(msg=server_status_messages.LIMIT_TRIES, code=401)

            remember_logged_in_user(driver, email, password)

        # in the web app now get the logged in user details

        active_fab.element_actions.wait_for_page_to_load_first_time_after_login(active_fab)

        if not active_fab.element_actions.check_if_web_app_is_available():
            return jsonify(msg=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)
        # active_fab.element_actions.wait_for_page_to_load()

        active_fab.element_actions.remove_unexpected_popups()
        if first_time_login:
            update_db_user_platform(active_fab)
            update_db_username(active_fab)
        existing_user = get_user_from_db_if_exists(email, password)
        append_new_fab_after_auth_success(active_fab, existing_user)

        access_token = create_access_token({'id': str(existing_user["_id"])}, expires_delta=datetime.timedelta(hours=1))
        return jsonify(msg=server_status_messages.SUCCESS_AUTH, code=200, token=access_token)

    except TimeoutException:
        print(f"Oops :( Something went wrong..")
        return jsonify(msg=server_status_messages.FAB_LOOP_FAILED, code=401)
    except Exception as e:
        print(e)
        return jsonify(msg=server_status_messages.DRIVER_ERROR, code=503)


def remember_logged_in_user(driver, email, password):
    eaCookies = driver.get_cookies()
    driver.get(app.SIGN_IN_URL)
    signInCookies = driver.get_cookies()

    for cookie in signInCookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        if cookie not in eaCookies:
            eaCookies.append(cookie)

    # update the db
    register_new_user_to_db(email, password, eaCookies)

    set_auth_status(email, True)
    driver.back()


def wait_for_status_code_loop(email):
    while not user_login_attempts[email].is_authenticated:
        if not user_login_attempts[email].tries_with_status_code:
            del active_fabs[email]
            return False
    return True
