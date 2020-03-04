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
        #trying to get rid of this down here with wait_for_element_disapears function - no success
        time.sleep(15)
        # element_actions.wait_for_element_disapears(elements.LOADING_CLASS,elements.LOADING_BACKDROP)
        element_actions.execute_element_action(elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)


        # click on search on transfer market
        element_actions.execute_element_action(elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)


        # write the searched player name
        element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)

        # choose the player in the list(the first one)
        element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)


        # set max BIN price - clear the input first
        element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

        # time.sleep(1)

        # set min price - clear the input first
        element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)


    def search_player(self, bin_increase=True):
        # search`
        element_actions = ElementActions(self.driver)
        element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)

        if bin_increase:
            element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
        else:
            element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)

    def buy_player(self):
        element_actions = ElementActions(self.driver)
        no_results_banner = element_actions.get_clickable_element(elements.NO_RESULTS_FOUND)
        if no_results_banner:
            element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return False
        else:
            element_actions.execute_element_action(elements.BUY_BTN, ElementCallback.CLICK)
            element_actions.execute_element_action(elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
            return True

        # if no players to the wanted price were found - navigate back

    def list_player(self, price):
        element_actions = ElementActions(self.driver)
        # Button to start the listing quickly after buying (not through user transfer list)
        element_actions.execute_element_action(elements.LIST_ON_TRANSFER_BTN, ElementCallback.CLICK)

        element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)


        element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)


        # List player on transfer market
        element_actions.execute_element_action(elements.LIST_ITEM_ON_TRANSFER_LIST, ElementCallback.CLICK)

        # Navigate back after player was listed
        element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
