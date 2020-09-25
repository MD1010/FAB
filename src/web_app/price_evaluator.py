import json

import requests

from consts import EA_TAX, PROFIT_MULTIPLIER, FUTBIN_PLAYER_PRICE_URL
from consts import MAX_PRICE, SANITY_PRICE_RATIO


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


def get_sell_price(market_price):
    prices = [[x for x in range(0, 1000, 50)],
              [x for x in range(1000, 10001, 100)],
              [x for x in range(10000, 50001, 250)],
              [x for x in range(50000, 100001, 500)],
              [x for x in range(100000, 15000001, 1000)]]

    for price_entry in prices:
        if market_price > max(price_entry):
            continue
        else:
            start_price_index = price_entry.index(min(price_entry, key=lambda price: abs(market_price - price)))
            start_price = price_entry[start_price_index - 2]
            buy_now = price_entry[start_price_index - 1]
            if start_price < 200: start_price = 200
            if buy_now < 250: buy_now = 250
            return start_price, buy_now


def get_max_buy_now_price(item_market_price):
    return item_market_price * EA_TAX - item_market_price * PROFIT_MULTIPLIER
