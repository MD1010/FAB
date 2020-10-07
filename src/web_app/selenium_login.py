from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from urllib3.exceptions import MaxRetryError

from consts import server_status_messages, app, elements, FUT_HOST
from src.accounts.ea_account_actions import check_account_if_exists, register_new_ea_account
from src.web_app.live_logins import login_attempts, authenticated_accounts
from utils.driver import create_driver_instance, close_driver, add_running_account
from utils.element_manager import ElementActions, ElementCallback
from utils.exceptions import UserNotFound, WebAppLoginError, AuthCodeRequired
from utils.helper_functions import server_response


class SeleniumLogin:

    def __init__(self, owner, email, password):
        self.email = email
        self.password = password
        self.owner = owner
        self.element_actions = None
        self.driver = None
        self.sid = None
        self.fut_host = None
    # exported to api
    def web_app_login(self, email):
        try:
            # first login try
            add_running_account(email)
            self.driver = create_driver_instance(email)
            self.element_actions = ElementActions(self.driver)

            existing_account = check_account_if_exists(email)

            if existing_account:
                self.login_with_cookies(existing_account["cookies"])
            else:  # login the first time
                self.login_first_time()
            return self._launch()

        except TimeoutException as e:
            close_driver(email)
            return server_response(code=503, error=server_status_messages.COULD_NOT_GET_SID)
        except UserNotFound as e:
            close_driver(email)
            return server_response(code=401, error=e.reason)
        except AuthCodeRequired as e:
            return server_response(msg=e.reason)
        except WebAppLoginError as e:
            close_driver(email)
            return server_response(code=e.code, error=e.reason)
        except MaxRetryError as e:
            close_driver(email)
            return server_response(code=503, error=server_status_messages.DRIVER_OPEN_FAIL)

    # exported to api
    def login_with_code(self, email, auth_code):
        try:
            self._set_status_code(auth_code)
            self._remember_account()
            return self._launch()
        except TimeoutException as e:
            close_driver(self.email)
            return server_response(code=503, error=server_status_messages.COULD_NOT_GET_SID)
        except WebAppLoginError as e:
            # dont close the driver if code is incorrect
            if e.reason != server_status_messages.WRONG_STATUS_CODE:
                close_driver(email)
            return server_response(code=e.code, error=e.reason)
        except MaxRetryError as e:
            close_driver(email)
            return server_response(code=503, error=server_status_messages.DRIVER_OPEN_FAIL)

    def _launch(self):
        self.element_actions.check_if_web_app_is_available()
        self._set_sid_from_requests()
        self._set_fut_host()
        self._add_authenticated_ea_account()
        close_driver(self.email)
        print("sid = " + self.sid) if self.sid else print("NO SID found")
        if self.sid:
            return server_response(msg=server_status_messages.LOGIN_SUCCESS, code=200)
        raise WebAppLoginError(reason=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)

    def _set_status_code(self, auth_code):
        self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")

        self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                                    auth_code)
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        self._raise_if_login_error_label_exists()
        self.is_status_code_set = True

    def login_with_cookies(self, cookies):
        # self.driver.delete_all_cookies()
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            self.driver.add_cookie(cookie)
        self.driver.get(app.WEB_APP_URL)

        self.element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)
        # Entering password left, and you are in!
        self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, self.password)
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        self._raise_if_login_error_label_exists()
        login_attempts[self.email] = self

    def login_first_time(self):
        self.driver.get(app.SIGN_IN_URL)
        self.element_actions.execute_element_action(elements.EMAIL_FIELD, ElementCallback.SEND_KEYS, self.email)
        self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, self.password)
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        self._raise_if_login_error_label_exists()
        # check the SMS option
        self.element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
        # send the sms verfication
        self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
        # save the login attempt if the credentials were ok
        login_attempts[self.email] = self
        raise AuthCodeRequired()

    def _remember_account(self):
        ea_cookies = self.driver.get_cookies()
        self.driver.get(app.SIGN_IN_URL)
        sign_in_cookies = self.driver.get_cookies()

        for cookie in sign_in_cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            if cookie not in ea_cookies:
                ea_cookies.append(cookie)

        # update the db
        register_new_ea_account(self.owner, self.email, self.password, ea_cookies)
        # enter the web app
        self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, self.password)
        self.element_actions.execute_element_action(elements.LOGIN_BTN, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.LOGIN_ENTER_APP, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, self.password)
        self.element_actions.execute_element_action(elements.LOGIN_BTN, ElementCallback.CLICK)

    def _raise_if_login_error_label_exists(self):
        login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
        code_error = self.element_actions.get_element(elements.CODE_ERROR)
        if login_error:
            raise WebAppLoginError(code=401, reason=server_status_messages.LOGIN_FAILED)
        if code_error:
            raise WebAppLoginError(code=401, reason=server_status_messages.WRONG_STATUS_CODE)
            # socketio.emit('wrong_code')

    def _set_sid_from_requests(self):
        for request in self.driver.requests:
            if str(request.path).endswith('fut.ea.com/ut/auth'):
                self.sid = request.response.headers.get('X-UT-SID')
                break

    def _add_authenticated_ea_account(self):
        authenticated_accounts[self.email] = self.email

    def _set_fut_host(self):
        self.element_actions.execute_element_action(elements.SETTINGS_ICON_OPEN_WEB_APP, ElementCallback.CLICK)
        platform_element = self.element_actions.get_element(elements.PLATFORM_ICON)
        platform = platform_element.get_attribute("class").split()[1]
        self.fut_host = FUT_HOST[platform]
