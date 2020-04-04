from active.data import users_attempted_login
from auth.auth_status import set_auth_status
from consts import elements, app
from elements.actions_for_execution import ElementCallback
from utils.driver import Driver


class SeleniumLogin(Driver):
    def __init__(self, driver, element_actions):
        super().__init__(driver)
        self.element_actions = element_actions

    def login_with_cookies(self, password, email, cookies):
        self.driver.delete_all_cookies()

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
            # check the SMS option
            self.element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
            # send the sms verfication
            self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
            # todo: return this lines after checking first time login.
            return True
        return False

    def _is_login_error_exists(self,email):
        login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
        if login_error:
            set_auth_status(email, False)
            return True
        return False

def set_status_code(fab, email, code, socketio, room_id):
    fab.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                                code)
    fab.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    status_code_error = fab.element_actions.get_element(elements.CODE_ERROR)
    if not status_code_error:
        set_auth_status(fab.driver, True)
        return True
    socketio.send("Wrong code!", room=room_id)
    users_attempted_login[email].tries_with_status_code -= 1
    return False