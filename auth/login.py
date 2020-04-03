import datetime
import gc
import time
from functools import wraps

import bcrypt
from flask import jsonify
from flask_jwt_extended import create_access_token
from selenium.common.exceptions import TimeoutException

from active.data import opened_drivers, active_fabs, active_login_sessions
from auth.login_attempt import LoginAttempt
from consts import server_status_messages, app, elements
from consts.app import TIME_TO_LOGIN
from elements.elements_manager import ElementCallback, initialize_element_actions
from fab import Fab
from utils import db
from utils.driver import initialize_driver
from utils.globals import element_actions


def check_auth_status(func):
    @wraps(func)
    def determine_if_func_should_run(self, *args):
        if not self.is_authenticated:
            return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
        return func(self, *args)

    return determine_if_func_should_run




def start_login(email, password):
    if email in active_login_sessions:
        if time.time() - active_login_sessions.get(email).timer >= TIME_TO_LOGIN:
            gc.collect(active_login_sessions.get(email))
            del active_login_sessions[email]
            return jsonify(msg=server_status_messages.TIME_OUT_LOGIN, code=401)


    existing_user = get_user_details_if_exists(email, password)
    # todo remove this to separate route.
    # todo create fab object with the id from the db and append it to the running fubs object.
    # if not user_details:
    #     return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)  # remove this too.
    try:
        # todo if a customer trying to enter to loged user, dont allow it.
        # initialize_user_details(self, user_details)
        if email in opened_drivers:
            driver = opened_drivers.get(email)
        else:
            driver = initialize_driver(email)
            login_session = LoginAttempt()
            active_login_sessions[email] = login_session
            initialize_element_actions(driver)

        if existing_user:
            # if check_if_user_has_saved_cookies(email, password):
            if not login_with_cookies(driver, password,  existing_user["cookies"]):

                return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
            fab = Fab(driver=driver, is_authenticated=True)
            active_fabs[existing_user["_id"]] = fab
            # todo 1.get id of current loged in user from db.
            # todo 2. data.active_fabs[id] = current_fab(that initialized till now with driver and is_authenticated turned to true.)

        # cookies file was not found - log in the first time
        else:
            if not is_login_successfull_from_first_time(self, email, password):
                return jsonify(msg=server_status_messages.FAILED_AUTH, code=401)
            # todo if login was successfuly save to db
            # todo 1.get id of current loged in user from db.
            # todo 2. data.active_fabs[id] = current_fab(that initialized till now with driver and is_authenticated turned to true.)
            while not self.is_authenticated:
                if not self.tries_with_status_code:
                    return jsonify(msg=server_status_messages.LIMIT_TRIES, code=401)
                # todo check if driver opened more than specific time.

            remember_logged_in_user(self)
        access_token = create_access_token({'id': str(user_details["_id"])},
                                           expires_delta=datetime.timedelta(hours=1))
        return jsonify(msg=server_status_messages.SUCCESS_AUTH, code=200, token=access_token)


    except TimeoutException:
        print(f"Oops :( Something went wrong..")
        return jsonify(msg=server_status_messages.FAB_LOOP_FAILED, code=401)
    except Exception as e:
        print(e)
        return jsonify(msg=server_status_messages.DRIVER_ERROR, code=503)


def get_user_details_if_exists(email, password):
    user_in_db = db.users_collection.find_one({"email": email})
    if not user_in_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        # The class user_details must store unhashed password in order to send to selenium an unhashed version
        return user_in_db
    else:
        return None


def check_if_user_has_saved_cookies(email, password):
    user_details = get_user_details_if_exists(email, password)
    if user_details is None:
        return False
    return True if len(user_details["cookies"]) > 0 else False


def initialize_user_details(self, user_details):
    self.connected_user_details = user_details


def set_auth_status(self, is_auth):
    self.is_authenticated = is_auth


def set_status_code(self, code, socketio, room_id):
    self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                                code)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    status_code_error = self.element_actions.get_element(elements.CODE_ERROR)
    if not status_code_error:
        set_auth_status(self, True)
        return True
    socketio.send("Wrong code!", room=room_id)
    self.tries_with_status_code -= 1
    return False


def login_with_cookies(driver, password, cookies):
    driver.delete_all_cookies()

    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        driver.add_cookie(cookie)
    driver.get(app.WEB_APP_URL)

    element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)
    # Entering password left, and you are in!
    element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
    element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if is_login_error_exists(driver):
        return False
    set_auth_status(driver, True)
    return True


def is_login_successfull_from_first_time(self, email, password):
    self.driver.get(app.SIGN_IN_URL)
    self.element_actions.execute_element_action(elements.EMAIL_FIELD, ElementCallback.SEND_KEYS, email)
    self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if not is_login_error_exists(self):
        # check the SMS option
        self.element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
        # send the sms verfication
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        # todo: return this lines after checking first time login.
        return True
    return False


def remember_logged_in_user(self):
    eaCookies = self.driver.get_cookies()
    self.driver.get(app.SIGN_IN_URL)
    signInCookies = self.driver.get_cookies()

    for cookie in signInCookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        if cookie not in eaCookies:
            eaCookies.append(cookie)
    # takes 10-15 secs
    # saveToCookiesFile(eaCookies, app.COOKIES_FILE_NAME)
    # update the user connected in fab class
    self.connected_user_details["cookies"] = eaCookies
    # update the db
    user_id = self.connected_user_details["_id"]
    db.users_collection.update({"_id": user_id}, {"$set": {"cookies": eaCookies}})
    set_auth_status(self, True)
    self.driver.back()


def is_login_error_exists(self):
    login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
    if login_error:
        set_auth_status(self, False)
        return True
    return False
