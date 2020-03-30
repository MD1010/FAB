from functools import wraps

import bcrypt

from consts import server_status_messages, app, elements
from elements.elements_manager import ElementCallback
from utils import db
from utils.helper_functions import jsonify
from utils.server_status import ServerStatus


def check_auth_status(func):
    @wraps(func)
    def determine_if_func_should_run(self, *args):
        if self.is_authenticated:
            return func(self, *args)
        else:
            return jsonify(ServerStatus(server_status_messages.FAILED_AUTH, 401))

    return determine_if_func_should_run


def get_user_details_if_exists(email, password):
    user_in_db = db.users_collection.find_one({"email": email})
    if not user_in_db:
        return None
    if bcrypt.hashpw(password.encode('utf-8'), user_in_db["password"]) == user_in_db["password"]:
        # The class user_details must store unhashed password in order to send to selenium an unhashed version
        user_in_db["password"] = password
        return user_in_db
    else:
        return None


def check_if_user_has_saved_cookies(user_details):
    return True if len(user_details["cookies"]) > 0 else False


def _wait_for_code(self):
    while self.statusCode is '':
        pass
    self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS, self.statusCode)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if is_login_error_exists(self):
        return False
    set_auth_status(self, True)
    return True


def get_status_code_from_user(self):
    tries = 3
    while tries > 0:
        wait_for_code_response = _wait_for_code(self)
        if wait_for_code_response:
            break
        else:
            # emit wrong code was sent message...
            self.statusCode = ''
            tries -= 1
    if tries == 0:
        return False
    return True


def initialize_user_details(self, user_details):
    self.connected_user_details = user_details


def set_auth_status(self, is_auth):
    self.is_authenticated = is_auth


def set_status_code(self, code):
    self.statusCode = code
    return ServerStatus(server_status_messages.STATUS_CODE_SET_CORRECTLY, 200)


def login_with_cookies(self, user_details):
    self.driver.delete_all_cookies()
    cookies = user_details["cookies"]
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        self.driver.add_cookie(cookie)
    self.driver.get(app.WEB_APP_URL)

    self.element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)
    # Entering password left, and you are in!
    self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, user_details["password"])
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if is_login_error_exists(self):
        return False
    set_auth_status(self, True)
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
    self.driver.back()


def is_login_error_exists(self):
    login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
    if login_error:
        set_auth_status(self, False)
        return True
    return False
