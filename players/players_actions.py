from selenium.webdriver.common.keys import Keys

from consts import elements
from driver import Driver
from elements.elements_manager import ElementCallback, ElementActions


class PlayerActions(Driver):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.element_actions = ElementActions(self.driver)

    def init_search_player_info(self, player_name, player_price):
        # click on TRANSFERS
        self.element_actions.execute_element_action(elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)
        # click on search on transfer market
        self.element_actions.execute_element_action(elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)
        # write the searched player name
        # self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        # choose the player in the list(the first one)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        # set max BIN price - clear the input first
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

    def buy_player(self):
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        # not enoght money left
        if no_results_banner:
            return False
        if not no_results_banner:
            buy_btn = self.element_actions.get_element(elements.BUY_BTN)
            can_buy = buy_btn.is_enabled() if buy_btn else False
            if can_buy:
                self.element_actions.execute_element_action(elements.BUY_BTN, ElementCallback.CLICK)
                self.element_actions.execute_element_action(elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
                return True
            else:
                print("algorithm for searching the next player will run!")
                return False


    def list_player(self, price):
        # Button to start the listing quickly after buying (not through user transfer list)
        self.element_actions.execute_element_action(elements.LIST_ON_TRANSFER_BTN, ElementCallback.CLICK)
        # adjust BIN
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # adjust starting BIN
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # List player on transfer market
        self.element_actions.execute_element_action(elements.LIST_ITEM_ON_TRANSFER_LIST, ElementCallback.CLICK)
        # Navigate back after player was listed
        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
