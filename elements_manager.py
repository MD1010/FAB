import time
from enum import Enum

from selenium.common.exceptions import NoSuchElementException

class ElementPathBy(Enum):
    CLASS_NAME = 0
    XPATH = 1
    ID = 2
    
def throw_if_element_unreachable(get_element_func) -> "throws error if element is not found":
    print("in throw if element is unreachable")

    def throw(*args, **kwargs):
        try:
            return get_element_func(*args, **kwargs)
        except NoSuchElementException:
            print("Element {args[1]} was not found!")
            raise NoSuchElementException(f"Element {args[1]} was not found!")

    return throw


@throw_if_element_unreachable
def get_clickable_element(element_path_by: 'xpath/className/id path', 
                          path: 'actual element path', 
                          driver) -> "return the wanted element if exists":
    # check_element_in_local_storage()
    switcher = {
        ElementPathBy.CLASS_NAME: driver.find_element_by_class_name,
        ElementPathBy.XPATH: driver.find_element_by_xpath,
        ElementPathBy.ID: driver.find_element_by_id
    }
    return switcher[element_path_by](path)
    # if len(element_list_result) == 0:
    #     raise NoSuchElementException()
    # return element_list_result[element_index]