import datetime
from functools import wraps

from flask import jsonify
from flask_jwt_extended import create_access_token
from selenium.common.exceptions import TimeoutException

from active.data import opened_drivers, active_fabs, users_attempted_login
from auth.auth_status import set_auth_status
from auth.selenium_login import SeleniumLogin
from auth.signup import register_new_user_to_db
from consts import server_status_messages, app
from elements.elements_manager import ElementActions
from players.players_actions import PlayerActions
from user_info.user import update_user_platform, update_user_name, User
from utils.driver import initialize_driver, check_if_web_app_is_available
from utils.helper_functions import create_new_fab, get_user_from_db_if_exists


def check_auth_status(func):
    @wraps(func)
    def determine_if_func_should_run(self, *args):
        if not self.is_authenticated:
            return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
        return func(self, *args)

    return determine_if_func_should_run


def start_login(email, password):
    # if user exists in db then he must have already logged in before and he has cookies
    existing_user = get_user_from_db_if_exists(email, password)

    try:
        if email in opened_drivers:
            driver = opened_drivers.get(email)
        else:
            driver = initialize_driver(email)
        element_actions = ElementActions(driver)
        player_actions = PlayerActions(element_actions)
        selenium_login = SeleniumLogin(driver, element_actions)
        new_user = User(email)
        if existing_user:
            if not selenium_login.login_with_cookies(password, email, existing_user["cookies"]):
                return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)

            active_fab = create_new_fab(driver, element_actions, player_actions, new_user)

        # cookies file was not found - log in the first time
        else:
            if not selenium_login.login_first_time(email, password):
                return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)

            active_fab = create_new_fab(driver, element_actions, player_actions, new_user)

            while not users_attempted_login[email].is_authenticated:
                if not users_attempted_login[email].tries_with_status_code:
                    del active_fabs[email]
                    return jsonify(msg=server_status_messages.LIMIT_TRIES, code=401)

            existing_user = remember_logged_in_user(driver, email, password)

        active_fab.element_actions.wait_for_page_to_load()

        if not check_if_web_app_is_available(active_fab):
            return jsonify(msg=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)
        else:
            active_fab.element_actions.remove_unexpected_popups()
            update_user_platform(active_fab)
            update_user_name(active_fab)
            access_token = create_access_token({'id': str(existing_user["_id"])}, expires_delta=datetime.timedelta(hours=1))
            return jsonify(msg=server_status_messages.SUCCESS_AUTH, code=200, token=access_token)


    except TimeoutException:
        print(f"Oops :( Something went wrong..")
        return jsonify(msg=server_status_messages.FAB_LOOP_FAILED, code=401)
    except Exception as e:
        print(e)
        return jsonify(msg=server_status_messages.DRIVER_ERROR, code=503)


# def check_if_user_has_saved_cookies(email, password):
#     user_details = get_user_details_if_exists(email, password)
#     if user_details is None:
#         return False
#     return True if len(user_details["cookies"]) > 0 else False


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
    new_user = get_user_from_db_if_exists(email, password)

    # user_id = self.connected_user_details["_id"]
    # db.users_collection.update({"_id": user_id}, {"$set": {"cookies": eaCookies}})
    set_auth_status(email, True)
    driver.back()
    return new_user
