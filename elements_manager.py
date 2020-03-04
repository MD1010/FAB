import time
from enum import Enum
from functools import partial

from selenium.common.exceptions import TimeoutException

from driver import Driver

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait


class ElementPathBy(Enum):
    CLASS_NAME = 0
    XPATH = 1
    ID = 2


class ElementCallback(Enum):
    CLICK = 0
    SEND_KEYS = 1


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


def wait_untill_clickable(driver, timeout, actual_path):
    path_by = get_path_by(actual_path)
    try:
        # change this stupid logic
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, actual_path))) \
            if path_by == ElementPathBy.XPATH \
            else WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CLASS_NAME, actual_path)))
    except TimeoutException as e:
        if timeout == 60:  # stuck on login
            print("Unable to log into the web app")
        else:
            raise TimeoutException(f"{actual_path} element was not found - Timeout")


class ElementActions(Driver):
    def __init__(self, driver):
        super().__init__(driver)

    def get_clickable_element(self, actual_path) -> "return the wanted element if exists":
        path_by = get_path_by(actual_path)
        path_by_switcher = {
            ElementPathBy.CLASS_NAME: self.driver.find_elements_by_class_name,
            ElementPathBy.XPATH: self.driver.find_elements_by_xpath,
            ElementPathBy.ID: self.driver.find_elements_by_id
        }
        found_element = path_by_switcher[path_by](actual_path)
        if len(found_element) == 0:
            print(f"{actual_path} element was not found")
            return None
        return found_element[0]

    def wait_for_element_disapears(self, element_class_name, actual_path, timeout=40):
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, actual_path)))
            WebDriverWait(self.driver, timeout).until(lambda d: element_class_name not in el.get_attribute('class'))
        except TimeoutException as e:
            raise TimeoutException(e)

    def execute_element_action(self, actual_path, callback, *callback_params, timeout=40):
        try:
            wait_untill_clickable(self.driver, timeout, actual_path)
            web_element = self.get_clickable_element(actual_path)
            run_callback(web_element, callback, callback_params)
        except TimeoutException as e:
            raise TimeoutException(e.msg)
