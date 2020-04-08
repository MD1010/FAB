import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from elements.elements_manager import ElementCallback, ElementActions
from utils.helper_functions import get_coin_balance_from_web_app


class PlayerActions:
    def __init__(self, element_actions):
        self.element_actions = element_actions


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


    def buy_player(self, current_coin_balance):
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        # not enough money left
        if no_results_banner:
            return False, None
        # there is a result found - try to buy
        else:
            buy_btn = self.element_actions.get_element(elements.BUY_BTN)
            can_buy = buy_btn.is_enabled() if buy_btn else False
            if not can_buy:
                return False, None
            else:
                self.element_actions.execute_element_action(elements.BUY_BTN, ElementCallback.CLICK)
                self.element_actions.execute_element_action(elements.CONFIRM_BUY_BTN, ElementCallback.CLICK)
                time.sleep(1)
                new_coin_balance = get_coin_balance_from_web_app(self.element_actions)
                # market was not refreshed properly - not a real buy! - budget may be changed due to a sold player
                if new_coin_balance >= current_coin_balance:
                    return False, None
                bought_for_label = self.element_actions.get_element(elements.BOUGHT_FOR)
                if bought_for_label:
                    bought_for = int(str(bought_for_label.text).replace(',', ''))
                    return True, bought_for
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
