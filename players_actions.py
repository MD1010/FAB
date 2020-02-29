import time
from enum import Enum

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import elements
import elements_manager
from elements_manager import ElementPathBy

from driver import Driver

from elements_manager import ElementCallback, ElementActions, ElementPathBy


class PlayerActions(Driver):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)

    def init_search_player_info(self, player_name, player_price):
        # click on TRANSFERS
        element_actions = ElementActions(self.driver)
        element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)

        time.sleep(1)

        # click on search on transfer market
        element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)

        time.sleep(1)

        # write the searched player name
        element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        time.sleep(1)

        # choose the player in the list(the first one)
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)

        time.sleep(1)

        # set max BIN price - clear the input first
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

        # time.sleep(1)

        # set min price - clear the input first
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

        time.sleep(1)

    def search_player(self, bin_increase=True):
        # search`
        element_actions = ElementActions(self.driver)
        element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)

        if bin_increase:
            element_actions.execute_element_action(ElementPathBy.XPATH, elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
        else:
            element_actions.execute_element_action(ElementPathBy.XPATH, elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)

    def buy_player(self):
        element_actions = ElementActions(self.driver)
        no_results_banner = element_actions.get_clickable_element(ElementPathBy.XPATH, elements.NO_RESULTS_FOUND)
        if no_results_banner:
            element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return False
        else:
            element_actions.execute_element_action(ElementPathBy.XPATH, elements.BUY_BTN, ElementCallback.CLICK)
            # 1 - buy , 2-cancel - cancel when testing
            # buy the player

            element_actions.execute_element_action(ElementPathBy.XPATH, elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
            element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return True

        # if no players to the wanted price were found - navigate back

    def list_player(self, price):
        element_actions = ElementActions(self.driver)
        # Button to start the listing quickly after buying (not through user transfer list)
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.LIST_ON_TRANSFER_BTN, ElementCallback.CLICK)
        time.sleep(2)

        element_actions.execute_element_action(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)

        time.sleep(2)

        element_actions.execute_element_action(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)

        time.sleep(2)

        # List player on transfer market
        element_actions.execute_element_action(ElementPathBy.XPATH, elements.LIST_ITEM_ON_TRANSFER_LIST, ElementCallback.CLICK)
        time.sleep(2)

        # Navigate back after player was listed
        element_actions.execute_element_action(ElementPathBy.CLASS_NAME, elements.NAVIGATE_BACK, ElementCallback.CLICK)
