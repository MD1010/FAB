import time
from enum import Enum
from functools import partial
from driver import Driver

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
    #delay after element is found - remove it - only needed in the first login
    time.sleep(0.8)
    action_switcher = {
        ElementCallback.CLICK: web_element.click,
        # may cause error because callback_params needs to be [0] - control A is an exception
        ElementCallback.SEND_KEYS: partial(web_element.send_keys, callback_params[0])
    }
    return action_switcher[callback]()

class ElementActions(Driver):
    def __init__(self,driver):
        super().__init__(driver)

    def get_clickable_element(self,path_by, actual_path) -> "return the wanted element if exists":
        path_by_switcher = {
            ElementPathBy.CLASS_NAME: self.driver.find_elements_by_class_name,
            ElementPathBy.XPATH: self.driver.find_elements_by_xpath,
            ElementPathBy.ID: self.driver.find_elements_by_id
        }
        found_element = path_by_switcher[path_by](actual_path)
        if len(found_element) == 0:
            return None
        return found_element[0]


    def execute_element_action(self, path_by, actual_path, callback, *callback_params):
        web_element = self.get_clickable_element(path_by, actual_path)
        run_callback(web_element, callback, callback_params)
