import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from enums.actions_for_execution import ElementCallback
from models.market_search import MarketSearch


class SearchFilterSetter(MarketSearch):
    def __init__(self, element_actions, custom_filters=None):
        if custom_filters is None:
            custom_filters = []
        self.custom_filters = custom_filters
        self.element_actions = element_actions

    def set_name_and_price_filters(self, item_name, player_price):
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS,
                                                    item_name)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
                                                    str(player_price))

    def set_custom_filters(self):
        pass