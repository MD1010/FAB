import json

import requests

from consts import elements
from consts.app import NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH, FUTBIN_PLAYER_PRICE_URL
from consts.prices import MIN_PRICE, MAX_PRICE, SANE_PRICE_RATIO
from enums.actions_for_execution import ElementCallback
from items.item_prices import check_item_RT_price, get_player_min_price_on_page
from players.player_data import build_player_objects_from_dict
from players.player_search import init_new_search
from user_info.user_actions import get_db_user_platform


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


def get_all_players_RT_prices(fab, required_items):
    RT_prices = []
    required_items = build_player_objects_from_dict(required_items)
    for item_obj in required_items:
        player_futbin_price = get_approximate_min_price_from_futbin(fab.user.email, item_obj)
        init_new_search(fab, item_obj, player_futbin_price)
        real_price = check_item_RT_price(fab, player_futbin_price)
        RT_prices.append({item_obj["name"]: real_price})
    return RT_prices


def get_approximate_min_price_from_futbin(user_email, player_obj):
    player_prices = []
    required_prices = ['LCPrice', 'LCPrice2', 'LCPrice3']

    player_id = str(player_obj["id"])
    url_of_specific_player_prices = f'{FUTBIN_PLAYER_PRICE_URL}{player_id}'
    prices_of_specific_player = json.loads(requests.get(url_of_specific_player_prices).content)

    for LCPrice in required_prices:
        if prices_of_specific_player[player_id] is None:
            player_prices.append(0)
        else:
            user_platform = get_db_user_platform(user_email)
            player_prices.append(prices_of_specific_player[player_id]['prices'][user_platform][LCPrice])

    for price_index in range(len(player_prices)):
        if ',' in str(player_prices[price_index]):
            player_prices[price_index] = player_prices[price_index].replace(',', '')
    price_after_sanity = _min_price_after_prices_sanity_check(player_prices)
    return price_after_sanity


