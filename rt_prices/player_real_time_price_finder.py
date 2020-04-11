import json

import requests

from consts.app import FUTBIN_PLAYER_PRICE_URL
from consts.prices.prices_consts import MAX_PRICE, SANE_PRICE_RATIO
from rt_prices.rt_price_finder import FutbinPriceFinder
from user_info.user_actions import get_db_user_platform


def _min_player_prices_after_sanity_check(player_prices):
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


class PlayerFutbinPriceFinder(FutbinPriceFinder):

    def get_futbin_price(self, item, user_email):
        player_prices = []
        required_prices = ['LCPrice', 'LCPrice2', 'LCPrice3']

        player_id = str(item.id)
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
        price_after_sanity = _min_player_prices_after_sanity_check(player_prices)
        return price_after_sanity
