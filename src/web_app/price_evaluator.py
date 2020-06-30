import json

import requests

from consts import DECREASE_SALE_PRICE_PERCENTAGE, MAP_INC_DEC_PRICES, MAX_PRICE, SANITY_PRICE_RATIO
from consts import EA_TAX, PROFIT_MULTIPLIER, FUTBIN_PLAYER_PRICE_URL


# this function adjusts that the futbin prices are up to date and if not it adjust
def _adjust_futbin_prices_if_outdated(futbin_prices):
    futbin_prices = [int(price) for price in futbin_prices]
    if futbin_prices[0] == 0:
        return MAX_PRICE
    else:
        for price_index in range(len(futbin_prices) - 1):
            try:
                if futbin_prices[price_index] / futbin_prices[price_index + 1] > SANITY_PRICE_RATIO:
                    return futbin_prices[price_index]
            except ZeroDivisionError:
                return futbin_prices[price_index]
        return futbin_prices[len(futbin_prices) - 1]


def get_futbin_price(def_id, platform):
    player_id = str(def_id)
    player_prices = []
    required_prices = ['LCPrice', 'LCPrice2', 'LCPrice3']

    # player_id = _get_player_attribute_from_json(full_name, revision_type, 'def_id')

    url_of_specific_player_prices = f'{FUTBIN_PLAYER_PRICE_URL}{player_id}'
    prices_of_specific_player = json.loads(requests.get(url_of_specific_player_prices).content)

    for LCPrice in required_prices:
        if prices_of_specific_player[player_id] is None:
            player_prices.append(0)
        else:
            player_prices.append(prices_of_specific_player[player_id]['prices'][platform][LCPrice])

    for price_index in range(len(player_prices)):
        if ',' in str(player_prices[price_index]):
            player_prices[price_index] = player_prices[price_index].replace(',', '')
    futbin_final_price = _adjust_futbin_prices_if_outdated(player_prices)
    return futbin_final_price

def get_start_price():
    pass
def get_max_bin_price():
    pass

def get_sell_price(market_price):
    # todo: rewrite this
    list_price = market_price - (market_price * DECREASE_SALE_PRICE_PERCENTAGE)
    for diff_range in MAP_INC_DEC_PRICES.items():
        min_max_range = diff_range[0].split("-")
        min_range,max_range = min_max_range
        if float(min_max_range[0]) < list_price < float(min_max_range[1]):
            scale = float(diff_range[1])
            break
    deviation = list_price % scale
    if deviation == scale / 2:
        list_price = list_price + deviation
    elif deviation > scale / 2:
        list_price = list_price - deviation + scale
    else:
        list_price = list_price - deviation
    return list_price


def _get_max_buy_now_price(item_market_price):
    return item_market_price * EA_TAX - item_market_price * PROFIT_MULTIPLIER
