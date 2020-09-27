from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from consts import server_status_messages, app, elements, FUT_HOST
from src.web_app.live_logins import login_attempts, authenticated_accounts
from utils.driver import get_or_create_driver_instance, close_driver
from src.accounts.ea_account_actions import check_account_if_exists, register_new_ea_account
from utils.element_manager import ElementActions, ElementCallback
from utils.exceptions import UserNotFound, WebAppLoginError
from utils.helper_functions import server_response


class SeleniumLogin:

    def __init__(self, owner, email, password, platform):
        self.email = email
        self.password = password
        self.owner = owner
        self.element_actions = None
        self.driver = None
        self.is_status_code_set = None
        self.sid = None
        self.platform = platform
        # get the platform from the html
        self.fut_host = FUT_HOST[platform]

    # exported to api
    def start_login(self, email):
        # if user exists in db then he must have already logged in before and he has cookies
        try:
            # todo: check if the account belongs to the owner
            existing_account = check_account_if_exists(email)

            self.driver = get_or_create_driver_instance(email)
            self.element_actions = ElementActions(self.driver)
            if existing_account:
                self.login_with_cookies(existing_account["cookies"])
            else:  # login the first time
                self.login_first_time()
                self._wait_for_status_code_loop()
                self._remember_account()

            self.element_actions.check_if_web_app_is_available()
            self.set_sid_from_requests()
            self.add_authenticated_ea_account()
            close_driver(email)
            print("sid = " + self.sid) if self.sid else print("NO SID found")
            if self.sid:
                return server_response(msg=server_status_messages.LOGIN_SUCCESS, code=200)
            raise WebAppLoginError(reason=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)

        except TimeoutException as e:
            close_driver(email)
            return server_response(code=503, error=server_status_messages.COULD_NOT_GET_SID)
        except UserNotFound as e:
            close_driver(email)
            return server_response(code=401, error=e.reason)
        except WebAppLoginError as e:
            close_driver(email)
            return server_response(code=e.code, error=e.reason)

    def set_status_code(self, status_code):
        try:
            self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                                        Keys.CONTROL, "a")

            self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS,
                                                        status_code)
            self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
            self._raise_if_login_error_label_exists()
            self.is_status_code_set = True
        except WebAppLoginError as e:
            return server_response(code=401, message=e.reason)
        return server_response(code=200, message=server_status_messages.STATUS_CODE_SET_CORRECTLY)

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

        self.driver.back()

    def _wait_for_status_code_loop(self):
        while not self.is_status_code_set:
            pass

    def _raise_if_login_error_label_exists(self):
        login_error = self.element_actions.get_element(elements.LOGIN_ERROR)
        code_error = self.element_actions.get_element(elements.CODE_ERROR)
        if login_error:
            raise WebAppLoginError(code=401, reason=server_status_messages.LOGIN_FAILED)
        if code_error:
            raise WebAppLoginError(code=401, reason=server_status_messages.WRONG_STATUS_CODE)

    def set_sid_from_requests(self):
        self.driver.wait_for_request('https://utas.external.s3.fut.ea.com/ut/auth')
        for request in self.driver.requests:
            if request.path == 'https://utas.external.s3.fut.ea.com/ut/auth':
                self.sid = request.response.headers.get('X-UT-SID')
                break

    def add_authenticated_ea_account(self):
        authenticated_accounts[self.email] = self.email
