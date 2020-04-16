import time
from functools import partial

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from consts import elements
from consts.app import TIME_TO_LOGIN, MAX_TIME_WAIT_FOR_PAGE
from consts.elements import START_ITEM_PRICE_ON_PAGE, END_ITEM_PRICE_ON_PAGE
from consts.selenium_scripts import REMOVE_ELEMENT
from enums.actions_for_execution import ElementCallback
from enums.path_by import ElementPathBy
from models.driver import Driver
from user_info.user_actions import update_db_coins_earned, update_db_total_runtime
from utils.driver_functions import close_driver


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


class ElementActions(Driver):
    def __init__(self, driver):
        super().__init__(driver)

    def get_element(self, actual_path) -> "return the wanted element if exists":
        path_by = get_path_by(actual_path)
        path_by_switcher = {
            ElementPathBy.CLASS_NAME: self.driver.find_elements_by_class_name,
            ElementPathBy.XPATH: self.driver.find_elements_by_xpath
        }
        found_element = path_by_switcher[path_by](actual_path)
        if len(found_element) == 0:
            print(f"{actual_path} element was not found")
            return None
        return found_element[0]

    def select_matching_li_by_text_from_dropdown_ul_list(self, open_dropdown_btn_path, ul_list_dropdown_path, desired_text):
        self.execute_element_action(open_dropdown_btn_path, ElementCallback.CLICK)
        dropdown_list = self.get_element(ul_list_dropdown_path)
        dropdown_options = dropdown_list.find_elements_by_tag_name("li")
        for option in dropdown_options:
            if str(option.text).lower() == str(desired_text).lower():
                option.click()
                break

    def wait_for_page_to_load(self, timeout=40):
        try:
            WebDriverWait(self.driver, timeout).until_not(EC.presence_of_element_located((By.CLASS_NAME, "showing")))
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, elements.SCREEN_AFTER_LOADING)))

        except TimeoutException as e:
            raise TimeoutException(e)

    def execute_element_action(self, actual_path, callback, *callback_params, timeout=10):
        try:
            self.wait_untill_clickable(actual_path, timeout)
            web_element = self.get_element(actual_path)
            run_callback(web_element, callback, callback_params)
        except TimeoutException as e:
            raise TimeoutException(e.msg)

    def remove_unexpected_popups(self):
        popup = self.get_element(elements.VIEW_MODAL_CONTAINER)
        if popup:
            self.driver.execute_script(REMOVE_ELEMENT, popup)

    def wait_untill_clickable(self, actual_path, timeout=10):
        path_by = get_path_by(actual_path)
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, actual_path))) \
                if path_by == ElementPathBy.XPATH \
                else WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.CLASS_NAME, actual_path)))
        except TimeoutException as e:
            raise TimeoutException(f"{actual_path} element was not found - Timeout")

    def wait_until_visible(self, actual_path, timeout=10):
        path_by = get_path_by(actual_path)
        try:
            # change this stupid logic
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, actual_path))) \
                if path_by == ElementPathBy.XPATH \
                else WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, actual_path)))
        except TimeoutException as e:
            if timeout == 60:  # stuck on login
                print("Unable to log into the web app")
            else:
                raise TimeoutException(f"{actual_path} element was not found - Timeout")

    def wait_for_page_to_load_without_element_timeout(self, fab):
        start_time = time.time()
        while self.get_element("{}{}{}".format(START_ITEM_PRICE_ON_PAGE, 1,
                                               END_ITEM_PRICE_ON_PAGE)) is None and self.get_element(
            elements.NO_RESULTS_FOUND) is None and time.time() - start_time < MAX_TIME_WAIT_FOR_PAGE:
            print("waiting for element for:{}".format(time.time() - start_time))
            pass
        if time.time() - start_time > MAX_TIME_WAIT_FOR_PAGE:
            close_driver(self.driver, fab.user.email)

    def check_if_last_element_exist(self):
        while True:
            try:
                self.execute_element_action(elements.NEXT_BUTTON, ElementCallback.CLICK, timeout=0)
                return True

            except WebDriverException:
                if self.get_element(
                        "{}{}{}".format(START_ITEM_PRICE_ON_PAGE, 1, END_ITEM_PRICE_ON_PAGE)):
                    return False

    def check_if_web_app_is_available(self):
        getting_started = self.get_element(elements.GETTING_STARTED)
        logged_on_console = self.get_element(elements.LOGGED_ON_CONSOLE)
        login_captcha = self.get_element(elements.LOGIN_CAPTHA)
        login_popup = self.get_element(elements.LOGIN_POPUP)
        servers_down = self.get_element(elements.SERVERS_DOWN)
        if getting_started or logged_on_console or login_captcha or login_popup or servers_down:
            return False
        return True

    def wait_for_page_to_load_first_time_after_login(self):
        start_time = time.time()
        while time.time() - start_time < TIME_TO_LOGIN / 15:
            try:
                for i in range(3):
                    self.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK, timeout=0)
                    time.sleep(1)
                break

            except WebDriverException:
                print("loading page.. ")
                time.sleep(1)
