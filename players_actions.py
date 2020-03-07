from selenium.webdriver.common.keys import Keys

import elements
from driver import Driver
from elements_manager import ElementCallback, ElementActions, ElementPathBy


class PlayerActions(Driver):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.element_actions = ElementActions(self.driver)

    def init_search_player_info(self, player_name, player_price):
        # click on TRANSFERS

        #trying to get rid of this down here with wait_for_element_disapears function - no success
        self.element_actions.execute_element_action(elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)
        # click on search on transfer market
        self.element_actions.execute_element_action(elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)
        # write the searched player name
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        # choose the player in the list(the first one)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        # set max BIN price - clear the input first
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)
        # set min price - clear the input first
        # element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

    def buy_player(self):
        no_results_banner = self.element_actions.get_clickable_element(elements.NO_RESULTS_FOUND)
        if no_results_banner:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return False
        else:
            self.element_actions.execute_element_action(elements.BUY_BTN, ElementCallback.CLICK)
            self.element_actions.execute_element_action(elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
            return True

    def list_player(self, price):
        # Button to start the listing quickly after buying (not through user transfer list)
        self.element_actions.execute_element_action(elements.LIST_ON_TRANSFER_BTN, ElementCallback.CLICK)

        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)

        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # List player on transfer market
        self.element_actions.execute_element_action(elements.LIST_ITEM_ON_TRANSFER_LIST, ElementCallback.CLICK)
        # Navigate back after player was listed
        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
