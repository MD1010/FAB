import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from driver import Driver
from elements.elements_manager import ElementCallback, ElementActions
from user_info import user
from user_info.user import get_coin_balance


class PlayerActions(Driver):
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.element_actions = ElementActions(self.driver)

    def init_search_player_info(self, player_name, player_futbin_price):
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS,
                                                    player_name)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
                                                    Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS,
                                                    str(player_futbin_price))

    def buy_player(self):
        coin_balance_before_buy = user.coin_balance
        # give time for the elements in the page to render - if remove stale exception
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        # not enough money left
        if no_results_banner:
            return False, None
        if not no_results_banner:
            buy_btn = self.element_actions.get_element(elements.BUY_BTN)
            can_buy = buy_btn.is_enabled() if buy_btn else False
            if can_buy:
                self.element_actions.execute_element_action(elements.BUY_BTN, ElementCallback.CLICK)
                self.element_actions.execute_element_action(elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
                time.sleep(1)
                user.coin_balance = get_coin_balance(self)
                bought_for = coin_balance_before_buy - user.coin_balance
                return True, bought_for
            else:
                return False, None
        else:
            return False, None

    def list_player(self, price):
        # check if elemenet is listable - maybe if the time has expired..
        list_element = self.element_actions.get_element(elements.LIST_ON_TRANSFER_BTN)
        if not list_element:
            return
        # Button to start the listing quickly after buying (not through user transfer list)
        self.element_actions.execute_element_action(elements.LIST_ON_TRANSFER_BTN, ElementCallback.CLICK)
        # adjust BIN
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # adjust starting BIN
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, ElementCallback.SEND_KEYS, price)
        # List player on transfer market
        self.element_actions.execute_element_action(elements.LIST_ITEM_ON_TRANSFER_LIST, ElementCallback.CLICK)
        time.sleep(1)
