import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from consts.app import MAX_CARD_ON_PAGE, NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH
from consts.elements import START_PLAYER_PRICE_ON_PAGE, END_PLAYER_PRICE_ON_PAGE
from consts.prices import MIN_PLAYER_PRICE, MAX_PRICE, MIN_PRICE
from enums.actions_for_execution import ElementCallback
from utils.prices import calc_new_max_price, get_scale_from_dict

def _check_item_price_regular_search(element_actions, player_price):
    searchs = NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH
    found_correct_price = False
    for search in range(searchs):
        if int(str(player_price).replace(',', '')) == MIN_PRICE:
            return True, MIN_PRICE
        element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        element_actions.wait_for_page_to_load_without_timeout()
        no_results_banner = element_actions.get_element(elements.NO_RESULTS_FOUND)
        # check if the player is less than the approximate price or not
        if no_results_banner and found_correct_price:
            element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            return True, int(str(player_price).replace(',', ''))
        if no_results_banner:
            element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            element_actions.execute_element_action(elements.INCREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
            player_price = element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
        if not no_results_banner:

            is_last_element_exist = element_actions.check_if_last_element_exist()
            if not is_last_element_exist:
                return get_player_min_price_on_page(element_actions)

            element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
            # found finally a result save the price and update the flag
            # time.sleep(1)
            element_actions.wait_until_visible(elements.MAX_BIN_PRICE_INPUT)
            player_price = element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value")
            found_correct_price = True
            element_actions.execute_element_action(elements.DECREASE_MAX_PRICE_BTN, ElementCallback.CLICK)
    return False, player_price


def check_item_RT_price(element_actions, player_futbin_price):
    # get_approximate_min specific to player if it is a consumable then anotherfunction has to be called
    find_player_from_regular_search, player_price = _check_item_price_regular_search(element_actions, player_futbin_price)
    if find_player_from_regular_search:
        return player_price
    is_found_price, player_price = check_if_get_results_in_current_price(element_actions, player_price)
    if is_found_price:
        find_player_from_binary_search, min_price = check_player_price_binary_search(element_actions, player_price)
        return min_price
    else:
        return MAX_PRICE


def _change_max_bin_price(element_actions, new_price):
    element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.CLICK)
    element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
    time.sleep(0.5)
    element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(new_price))
    time.sleep(0.5)
    element_actions.execute_element_action(elements.SEARCH_PRICE_HEADER, ElementCallback.CLICK)
    return int(element_actions.get_element(elements.MAX_BIN_PRICE_INPUT).get_attribute("value").replace(',', ''))


def check_if_get_results_in_current_price(element_actions, player_price):
    element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    no_results_banner = element_actions.get_element(elements.NO_RESULTS_FOUND)
    while no_results_banner:
        player_price = player_price * 2
        player_price = _change_max_bin_price(element_actions, player_price)
        no_results_banner = element_actions.get_element(elements.NO_RESULTS_FOUND)
        if no_results_banner and player_price >= MAX_PRICE:
            return False, MAX_PRICE
    return True, player_price


def get_player_min_price_on_page(element_actions):
    min_prices_on_page = []
    for i in range(1, MAX_CARD_ON_PAGE + 1):
        if element_actions.get_element("{}{}{}".format(START_PLAYER_PRICE_ON_PAGE, i, END_PLAYER_PRICE_ON_PAGE)) is not None:
            min_prices_on_page.append(
                int(element_actions.get_element("{}{}{}".format(START_PLAYER_PRICE_ON_PAGE, i, END_PLAYER_PRICE_ON_PAGE)).text.replace(",", "")))
        else:
            break
    element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    return True, min(min_prices_on_page)


def check_player_price_binary_search(element_actions, player_price):
    down_limit = MIN_PLAYER_PRICE
    up_limit = int(player_price.replace(',', ''))
    player_new_max_price = calc_new_max_price(down_limit, up_limit, 0)
    search_scales = get_scale_from_dict(up_limit, down_limit)
    player_price_after_webapp_transfer = _change_max_bin_price(element_actions, player_new_max_price)
    element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    while up_limit - down_limit not in search_scales:
        element_actions.wait_for_page_to_load_without_timeout()
        is_no_results_banner = element_actions.get_element(elements.NO_RESULTS_FOUND)
        if is_no_results_banner:
            down_limit = player_price_after_webapp_transfer
            player_new_max_price = calc_new_max_price(down_limit, up_limit, 1)
            player_price_after_webapp_transfer = _change_max_bin_price(element_actions, player_new_max_price)

            search_scales = get_scale_from_dict(down_limit, up_limit)
        else:
            is_last_element_exist = element_actions.check_if_last_element_exist()
            if not is_last_element_exist:
                return get_player_min_price_on_page(element_actions)
            up_limit = player_price_after_webapp_transfer
            player_new_max_price = calc_new_max_price(down_limit, up_limit, 0)
            player_price_after_webapp_transfer = _change_max_bin_price(element_actions, player_new_max_price)

            search_scales = get_scale_from_dict(down_limit, up_limit)

        element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
    element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
    return True, up_limit
