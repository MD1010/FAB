import time
from enum import Enum
from functools import partial

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from consts import elements, server_status_messages, TIME_TO_LOGIN
from consts.elements import START_PLAYER_PRICE_ON_PAGE, END_PLAYER_PRICE_ON_PAGE
from src.app import socketio
from utils.exceptions import WebAppLoginError


class ElementCallback(Enum):
    CLICK = 0
    SEND_KEYS = 1


class ElementPathBy(Enum):
    CLASS_NAME = 0
    XPATH = 1


def run_callback(web_element, callback, *callback_params: 'price if sendKeys'):
    if web_element is None:
        return None

    action_switcher = {
        ElementCallback.CLICK: web_element.click,
        ElementCallback.SEND_KEYS:
            (
                lambda: partial(web_element.send_keys, callback_params[0])
                if len(callback_params) == 1
                else partial(web_element.send_keys, callback_params[0], callback_params[1])
            )()
    }

    return action_switcher[callback]()


def get_path_by(actual_path):
    if str(actual_path).startswith('/'):
        return ElementPathBy.XPATH
    else:
        return ElementPathBy.CLASS_NAME


class ElementActions:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def get_element(self, actual_path) -> "return the wanted element if exists":
        path_by = get_path_by(actual_path)
        path_by_switcher = {
            ElementPathBy.CLASS_NAME: self.driver.find_elements_by_class_name,
            ElementPathBy.XPATH: self.driver.find_elements_by_xpath
        }
        found_element = path_by_switcher[path_by](actual_path)
        if len(found_element) == 0:
            return None
        return found_element[0]

    def wait_for_page_to_load(self, timeout=40):
        try:
            WebDriverWait(self.driver, timeout).until_not(EC.presence_of_element_located((By.CLASS_NAME, "showing")))
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, elements.SCREEN_AFTER_LOADING)))

        except TimeoutException as e:
            raise TimeoutException(e)

    def execute_element_action(self, actual_path, callback, *callback_params, timeout=10):
        try:
            self._wait_untill_clickable(timeout, actual_path)
            web_element = self.get_element(actual_path)
            run_callback(web_element, callback, callback_params)
        except TimeoutException as e:
            raise TimeoutException(e.msg)

    def _wait_untill_clickable(self, timeout, actual_path):
        path_by = get_path_by(actual_path)
        try:
            # change this stupid logic
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, actual_path))) \
                if path_by == ElementPathBy.XPATH \
                else WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.CLASS_NAME, actual_path)))
        except TimeoutException as e:
            if timeout == 60:  # stuck on login
                print("Unable to log into the web app")
            else:
                raise TimeoutException(f"{actual_path} element was not found - Timeout")

    def wait_until_visible(self, actual_path, timeout=10):
        path_by = get_path_by(actual_path)
        try:
            # change this stupid logic
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, actual_path))) \
                if path_by == ElementPathBy.XPATH \
                else WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, actual_path)))
        except TimeoutException as e:
            if timeout == TIME_TO_LOGIN:  # stuck on login
                print("Unable to log into the web app")
            else:
                raise TimeoutException(f"{actual_path} element was not found - Timeout")

    def wait_for_page_to_load_without_timeout(self):
        while self.get_element("{}{}{}".format(START_PLAYER_PRICE_ON_PAGE, 1,
                                               END_PLAYER_PRICE_ON_PAGE)) is None and self.get_element(
            elements.NO_RESULTS_FOUND) is None:
            pass

    def check_if_web_app_is_available(self):
        self._wait_for_page_to_load_first_time_after_login()
        socketio.emit('captchaCheck', "checking for captchas...")
        getting_started = self.get_element(elements.GETTING_STARTED)
        logged_on_console = self.get_element(elements.LOGGED_ON_CONSOLE)
        login_captcha = self.get_element(elements.LOGIN_CAPTHA)
        login_popup = self.get_element(elements.LOGIN_POPUP)
        if getting_started or logged_on_console or login_captcha or login_popup:
            print("found captcha/login screen issue")
            raise WebAppLoginError(code=503, reason=server_status_messages.WEB_APP_NOT_AVAILABLE)

    def _wait_for_page_to_load_first_time_after_login(self):
        start_time = time.time()
        is_page_loaded = False
        while time.time() - start_time < TIME_TO_LOGIN and not is_page_loaded:
            try:
                self.remove_unexpected_popups()
                # blocked = when the web app has captcha or club does not exist message the settings icon is located in different place
                # opened = when the web app is fully loaded
                blocked_settings = self.get_element(elements.SETTINGS_ICON_BLOCKED_WEB_APP)
                opened_settings = self.get_element(elements.SETTINGS_ICON_OPEN_WEB_APP)

                if blocked_settings or opened_settings:
                    if blocked_settings:
                        self.execute_element_action(elements.SETTINGS_ICON_BLOCKED_WEB_APP, ElementCallback.CLICK)
                    else:
                        self.execute_element_action(elements.SETTINGS_ICON_OPEN_WEB_APP, ElementCallback.CLICK)
                    is_page_loaded = True
                else:
                    raise WebDriverException()
            except WebDriverException:
                time.sleep(1)

        if not is_page_loaded:
            raise WebAppLoginError(code=503, reason=server_status_messages.WEB_APP_NOT_AVAILABLE)

    def remove_unexpected_popups(self):
        remove_element_script = """var element = arguments[0];element.parentNode.removeChild(element);"""
        popup = self.get_element(elements.VIEW_MODAL_CONTAINER)
        if popup:
            self.driver.execute_script(remove_element_script, popup)
