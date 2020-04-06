import json
import time

import requests
from selenium.webdriver.common.keys import Keys

from consts import elements
from consts.app import NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH, MAX_CARD_ON_PAGE, FUTBIN_PLAYER_PRICE_URL
from consts.elements import START_PLAYER_PRICE_ON_PAGE, END_PLAYER_PRICE_ON_PAGE
from consts.prices import MIN_PRICE, MAP_INC_DEC_PRICES, MIN_PLAYER_PRICE, MAX_PRICE, SANE_PRICE_RATIO
from elements.actions_for_execution import ElementCallback
from utils.db import get_db_user_platform


def _check_player_RT_price(fab, player_obj):
    player_futbin_price = get_approximate_min_price(fab, player_obj)
    fab.player_actions.init_search_player_info(player_obj["name"], player_futbin_price)
    find_player_from_regular_search, player_price = check_player_price_regular_search(fab, player_futbin_price)
    if find_player_from_regular_search:
        return player_price
    is_found_price, player_price = check_if_get_results_in_current_price(fab, player_price)
    if is_found_price:
        find_player_from_binary_search, min_price = check_player_price_binary_search(fab, player_price)
        return min_price
    else:
        return MAX_PRICE


def _min_price_after_prices_sanity_check(player_prices):
    player_prices = [int(price) for price in player_prices]
    if player_prices[0] == 0:
        return MAX_PRICE
    else:
        for price_index in range(len(player_prices) - 1):
            try:
                if player_prices[price_index] / player_prices[price_index + 1] > SANE_PRICE_RATIO:
                    return player_prices[price_index]
            except ZeroDivisionError:
                return player_prices[price_index]
        return player_prices[len(player_prices) - 1]


def _get_player_min_price_on_page(fab):
    min_prices_on_page = []
    for i in range(1, MAX_CARD_ON_PAGE + 1):
        if fab.element_actions.get_element("{}{}{}".format(START_PLAYER_PRICE_ON_PAGE, i, END_PLAYER_PRICE_ON_PAGE)) is not None:
            min_prices_on_page.append(
                int(fab.element_actions.get_element("{}{}{}".format(START_PLAYER_PRICE_ON_PAGE, i, END_PLAYER_PRICE_ON_PAGE)).text.replace(",", "")))
        else:
            break
    fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    return True, min(min_prices_on_page)


def _calc_new_max_price(down_limit, up_limit, is_inc):
    if is_inc:
        return down_limit + abs(up_limit - down_limit) / 2
    else:
        return up_limit - abs(up_limit - down_limit) / 2

def _get_scale_from_dict(upper_bound, lower_bound):
    possible_scales = []
    for element in MAP_INC_DEC_PRICES.items():
        values = element[0].split("-")
        if int(values[0]) < upper_bound < int(values[1]):
            possible_scales.append(int(element[1]))
        elif int(values[0]) < lower_bound < int(values[1]):
            possible_scales.append(int(element[1]))
    return possible_scales


def _change_max_bin_price(fab, new_price):
    fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    fab.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.CLICK)
    fab.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
    time.sleep(0.5)
    fab.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(new_price))
    time.sleep(0.5)
    fab.element_actions.execute_element_action(elements.SEARCH_PRICE_HEADER, ElementCallback.CLICK)
    return int(fab.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value").replace(',', ''))


def get_all_players_RT_prices(fab, required_players):
    RT_prices = []
    for player_obj in required_players:
        real_price = _check_player_RT_price(fab, player_obj)
        RT_prices.append({player_obj["name"]: real_price})
    return RT_prices


def get_approximate_min_price(fab, player_obj):
    player_prices = []
    required_prices = ['LCPrice', 'LCPrice2', 'LCPrice3']

    player_id = str(player_obj["id"])
    url_of_specific_player_prices = f'{FUTBIN_PLAYER_PRICE_URL}{player_id}'
    prices_of_specific_player = json.loads(requests.get(url_of_specific_player_prices).content)

    for LCPrice in required_prices:
        if prices_of_specific_player[player_id] is None:
            player_prices.append(0)
        else:
            user_platform = get_db_user_platform(fab.user.email)
            player_prices.append(prices_of_specific_player[player_id]['prices'][user_platform][LCPrice])

    for price_index in range(len(player_prices)):
        if ',' in str(player_prices[price_index]):
            player_prices[price_index] = player_prices[price_index].replace(',', '')
    price_after_sanity = _min_price_after_prices_sanity_check(player_prices)
    return price_after_sanity


def check_player_price_regular_search(fab, player_price):
    searchs = NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH
    found_correct_price = False
    for search in range(searchs):
        if int(str(player_price).replace(',', '')) == MIN_PRICE:
            return True, MIN_PRICE
        fab.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        fab.element_actions.wait_for_page_to_load_without_timeout()
        no_results_banner = fab.element_actions.get_element(elements.NO_RESULTS_FOUND)
        # check if the player is less than the approximate price or not
        if no_results_banner and found_correct_price:
            fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return True, int(str(player_price).replace(',', ''))
        if no_results_banner:
            fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            fab.element_actions.execute_element_action(elements.INCREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
            player_price = fab.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
        if not no_results_banner:

            is_last_element_exist = fab.element_actions.check_if_last_element_exist()
            if not is_last_element_exist:
                return _get_player_min_price_on_page(fab)

            fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            # found finally a result save the price and update the flag
            # time.sleep(1)
            fab.element_actions.wait_until_visible(elements.MAX_BIN_PRICE_INPUT)
            player_price = fab.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
            found_correct_price = True
            fab.element_actions.execute_element_action(elements.DECREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
    return False, player_price


def check_player_price_binary_search(fab, player_price):
    down_limit = MIN_PLAYER_PRICE
    up_limit = int(player_price.replace(',', ''))
    player_new_max_price = _calc_new_max_price(down_limit, up_limit, 0)
    search_scales = _get_scale_from_dict(up_limit, down_limit)
    player_price_after_webapp_transfer = _change_max_bin_price(fab, player_new_max_price)
    fab.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    while up_limit - down_limit not in search_scales:
        fab.element_actions.wait_for_page_to_load_without_timeout()
        is_no_results_banner = fab.element_actions.get_element(elements.NO_RESULTS_FOUND)
        if is_no_results_banner:
            down_limit = player_price_after_webapp_transfer
            player_new_max_price = _calc_new_max_price(down_limit, up_limit, 1)
            player_price_after_webapp_transfer = _change_max_bin_price(fab, player_new_max_price)

            search_scales = _get_scale_from_dict(down_limit, up_limit)
        else:
            is_last_element_exist = fab.element_actions.check_if_last_element_exist()
            if not is_last_element_exist:
                return _get_player_min_price_on_page(fab)
            up_limit = player_price_after_webapp_transfer
            player_new_max_price = _calc_new_max_price(down_limit, up_limit, 0)
            player_price_after_webapp_transfer = _change_max_bin_price(fab, player_new_max_price)

            search_scales = _get_scale_from_dict(down_limit, up_limit)

        fab.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    return True, up_limit


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
