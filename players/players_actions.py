import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from consts.app import MIN_PRICE
from driver import Driver
from elements.elements_manager import ElementCallback, ElementActions
from players.player_search import get_approximate_min_price


class PlayerActions(Driver):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.element_actions = ElementActions(self.driver)

    def init_search_player_info(self, player_name, player_price):
        # write the searched player name
        # self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        # choose the player in the list(the first one)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        # set max BIN price - clear the input first
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, player_price)

        max_price_input = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute('value')
        if max_price_input != player_price:
            return False
        # self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        return True

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
                return False

    def list_player(self, price):
        # check if elemenet is listable - maybe if the time has expired..
        list_element = self.element_actions.get_element(elements.LIST_ON_TRANSFER_BTN)
        if not list_element:
            return
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

    def check_player_RT_price(self, player_name, player_revision):
        found_correct_price = False
        player_price = get_approximate_min_price(player_name, player_revision)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(player_price))
        while True:
            if int(str(player_price).replace(',','')) == MIN_PRICE:
                return MIN_PRICE
            self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
            time.sleep(1)
            no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
            # check if the player is less than the approximate price or not
            if no_results_banner and found_correct_price:
                return int(str(player_price).replace(',',''))
            if no_results_banner:
                self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
                self.element_actions.execute_element_action(elements.INCREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
                player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
            if not no_results_banner:
                self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
                #found finally a result save the price and update the flag
                player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
                found_correct_price = True
                self.element_actions.execute_element_action(elements.DECREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
