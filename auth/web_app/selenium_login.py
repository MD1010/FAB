from selenium.webdriver.common.keys import Keys

from auth.web_app.auth_status import set_auth_status
from consts.app import LOGIN_SIGN_BEFORE_STATUS_CODE_CHECK_OPTION
from live_data import ea_account_login_attempts
from consts import elements, app
from enums.actions_for_execution import ElementCallback
from models.driver import Driver
from utils.elements_manager import ElementActions


class SeleniumLogin(Driver):
    def __init__(self, driver, element_actions):
        super().__init__(driver)
        self.element_actions = element_actions

    def login_with_cookies(self, password, email, cookies):
        # self.driver.delete_all_cookies()

        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            self.driver.add_cookie(cookie)
        self.driver.get(app.WEB_APP_URL)

        self.element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)
        # Entering password left, and you are in!
        self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        if self._is_login_error_exists(email):
            return False
        set_auth_status(email, True)
        return True

    def login_first_time(self, email, password):

        self.driver.get(app.SIGN_IN_URL)
        self.element_actions.execute_element_action(elements.EMAIL_FIELD, ElementCallback.SEND_KEYS, email)
        self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        if not self._is_login_error_exists(email):
            login_message_before_status_code = self.element_actions.get_element(elements.LOGIN_MESSAGE).text
            if LOGIN_SIGN_BEFORE_STATUS_CODE_CHECK_OPTION in login_message_before_status_code:
                # check the SMS option
                self.element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
                # send the sms verfication
                self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
                # emit that code send to phone.
            else:
                self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
                # emit that code send to mail/phone/call to phone.

                # emit that code send to phone.

            # todo: return this lines after checking first time login.
            return True
        return False

    def _is_login_error_exists(self,email):
        login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
        if login_error:
            set_auth_status(email, False)
            return True
        return False

def set_status_code(driver, email, code, socketio, room_id):
    element_actions = ElementActions(driver)
    element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                               Keys.CONTROL, "a")
    element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                               code)


    element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    status_code_error = element_actions.get_element(elements.CODE_ERROR)
    if not status_code_error:
        set_auth_status(email, True)
        return True
    socketio.send("Wrong code!", room=room_id)
    ea_account_login_attempts[email].tries_with_status_code -= 1
    return False