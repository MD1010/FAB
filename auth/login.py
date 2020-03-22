from functools import wraps

from consts import server_status_messages, app, elements
from elements.elements_manager import ElementCallback
from helper_functions import loadCookiesFile, saveToCookiesFile

def check_auth_status(func):
    @wraps(func)
    def determine_if_func_should_run(self, *args):
        if self.is_authenticated:
            return func(self, *args)
        else:
            return server_status_messages.FAILED_AUTH, 401

    return determine_if_func_should_run

def set_auth_status(self, is_auth):
    self.is_authenticated = is_auth

def wait_for_code(self):
    while self.statusCode is '':
        pass
    self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS, self.statusCode)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if not check_for_login_error(self):
        self.set_status_code('')
        return False
    set_auth_status(self, True)
    return True

def login_with_cookies(self, password):
    self.driver.delete_all_cookies()
    cookies = loadCookiesFile(app.COOKIES_FILE_NAME)
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        self.driver.add_cookie(cookie)
    self.driver.get(app.WEB_APP_URL)

    self.element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)
    # Entering password left, and you are in!
    self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if not check_for_login_error(self):
        return False
    set_auth_status(self, True)
    return True

def login_first_time(self, email, password):
    self.driver.get(app.SIGN_IN_URL)
    self.element_actions.execute_element_action(elements.EMAIL_FIELD, ElementCallback.SEND_KEYS, email)
    self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    if not check_for_login_error(self):
        return False
    # check the SMS option
    self.element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
    # send the sms verfication
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    return True

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
    saveToCookiesFile(eaCookies, app.COOKIES_FILE_NAME)
    self.driver.back()

def check_for_login_error(self):
    login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
    if login_error:
        set_auth_status(self, False)
        return False
    return True