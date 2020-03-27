import time
from functools import partial

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from elements.models.actions_for_execution import ElementCallback
from elements.models.path_by import ElementPathBy
from scripts import selenium
from driver import Driver

from consts import elements


def initialize_element_actions(self):
    self.element_actions = ElementActions(self.driver)

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

    def wait_for_page_to_load(self, timeout=40):
        try:
            WebDriverWait(self.driver, timeout).until_not(EC.presence_of_element_located((By.CLASS_NAME, "showing")))
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, elements.SCREEN_AFTER_LOADING)))

        except TimeoutException as e:
            raise TimeoutException(e)

    def execute_element_action(self, actual_path, callback, *callback_params, timeout=10):
        try:
            self.wait_untill_clickable(timeout, actual_path)
            web_element = self.get_element(actual_path)
            run_callback(web_element, callback, callback_params)
        except TimeoutException as e:
            raise TimeoutException(e.msg)

    def remove_unexpected_popups(self):
        popup = self.get_element(elements.VIEW_MODAL_CONTAINER)
        if popup:
            self.driver.execute_script(selenium.REMOVE_ELEMENT, popup)

    def wait_untill_clickable(self,timeout, actual_path):
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
            if timeout == 60:  # stuck on login
                print("Unable to log into the web app")
            else:
                raise TimeoutException(f"{actual_path} element was not found - Timeout")
