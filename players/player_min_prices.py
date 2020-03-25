from selenium.webdriver.common.keys import Keys
from consts import elements
from consts.app import NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH
from consts.prices import MIN_PRICE, MAP_INC_DEC_PRICES, MIN_PLAYER_PRICE, MAX_PRICE
from elements.models.actions_for_execution import ElementCallback
import time


def check_player_price_regular_search(self, player_price):
    searchs = NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH
    found_correct_price = False
    for search in range(searchs):
        if int(str(player_price).replace(',', '')) == MIN_PRICE:
            return True, MIN_PRICE
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        time.sleep(1)
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        # check if the player is less than the approximate price or not
        if no_results_banner and found_correct_price:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return True, int(str(player_price).replace(',', ''))
        if no_results_banner:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            self.element_actions.execute_element_action(elements.INCREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
            player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
        if not no_results_banner:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            # found finally a result save the price and update the flag
            # time.sleep(1)
            self.element_actions.wait_until_visible(elements.MAX_BIN_PRICE_INPUT)
            player_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
            found_correct_price = True
            self.element_actions.execute_element_action(elements.DECREASE_MAX_PRICE_BTN, ElementCallback.CLICK)

    return False, player_price


def _get_scale_from_dict(self, upper_bound, lower_bound):
    possible_scales = []
    for element in MAP_INC_DEC_PRICES.items():
        values = element[0].split("-")
        if upper_bound > int(values[0]) and upper_bound < int(values[1]):
            possible_scales.append(int(element[1]))
        elif lower_bound > int(values[0]) and lower_bound < int(values[1]):
            possible_scales.append(int(element[1]))
    return possible_scales


def _calc_new_max_price(down_limit, up_limit, is_inc):
    if is_inc:
        return down_limit + abs(up_limit - down_limit) / 2
    else:
        return up_limit - abs(up_limit - down_limit) / 2


def check_player_price_binary_search(self, player_price):
    down_limit = MIN_PLAYER_PRICE
    up_limit = int(player_price.replace(',', ''))
    player_new_max_price = _calc_new_max_price(down_limit, up_limit, 0)
    search_scales = _get_scale_from_dict(self, up_limit, down_limit)
    player_price_after_webapp_transfer = _change_max_bin_price(self, player_new_max_price)
    self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    while up_limit - down_limit not in search_scales:
        time.sleep(1)
        is_no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        if is_no_results_banner:
            down_limit = player_price_after_webapp_transfer
            player_new_max_price = _calc_new_max_price(down_limit, up_limit, 1)
            player_price_after_webapp_transfer = _change_max_bin_price(self, player_new_max_price)

            search_scales = _get_scale_from_dict(self, down_limit, up_limit)
        else:
            up_limit = player_price_after_webapp_transfer
            player_new_max_price = _calc_new_max_price(down_limit, up_limit, 0)
            player_price_after_webapp_transfer = _change_max_bin_price(self, player_new_max_price)

            search_scales = _get_scale_from_dict(self, down_limit, up_limit)

        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    return True, up_limit


def _change_max_bin_price(self, new_price):
    self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.CLICK)
    self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
    time.sleep(1)
    self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(new_price))
    time.sleep(1)
    self.element_actions.execute_element_action(elements.SEARCH_PRICE_HEADER, ElementCallback.CLICK)
    return int(self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value").replace(',', ''))


def check_if_get_results_in_current_price(self, player_price):
    self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
    while no_results_banner:
        player_price = player_price * 2
        player_price = _change_max_bin_price(self, player_price)
        no_results_banner = self.element_actions.get_element(elements.NO_RESULTS_FOUND)
        if no_results_banner and player_price >= MAX_PRICE:
            return False, MAX_PRICE
    return True, player_price
