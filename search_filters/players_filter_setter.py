import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from consts import elements
from enums.actions_for_execution import ElementCallback
from models.search_filter_setter import SearchFilterSetter

from selenium.webdriver.support.ui import Select

class PlayerFilterSetter(SearchFilterSetter):
    def __init__(self, element_actions):
        self.element_actions = element_actions

    def set_specific_item_name_filter(self, player_name):
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)

    def set_item_quality_filter(self, player_quality):

        self.element_actions.execute_element_action(elements.PLAYER_QUALITY_FILTER_BTN,ElementCallback.CLICK)
        quality_dropdown = self.element_actions.get_element(elements.PLAYER_QUALITY_FILTER_DROPDOWN)
        dropdown_options = quality_dropdown.find_elements_by_tag_name("li")
        for option in dropdown_options:
            if option.text == player_quality:
                option.click()
                break


    def set_item_price_filter(self, player_price):
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(player_price))

    def set_player_position_filter(self, player_position):
        pass

    def set_player_chem_filter(self, player_chem):
        pass

    def set_player_nation_filter(self, player_nation):
        pass

    def set_player_league_filter(self, player_league):
        pass

    def set_player_club_filter(self, player_club):
        pass
