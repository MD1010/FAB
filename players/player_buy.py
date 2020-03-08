from consts import elements
from elements.elements_manager import ElementCallback
from consts.app import FUTBIN_PLAYER_PRICE_URL
import requests
import json


def decrease_increase_min_price(self, increase_price):
    # check if price can be decreased
    el = self.element_actions.get_clickable_element(elements.DECREASE_PRICE_BTN)
    can_be_decreased = el.is_enabled()
    max_bin_price = self.element_actions.get_clickable_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value")
    can_be_increased = True if max_bin != "200" else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        self.element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        self.element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)

def get_current_player_min_price(first_player_name, last_player_name, player_rating, *common_player_name):
    player =  {
      "c": "Cristiano Ronaldo",
      "f": "C. Ronaldo",
      "id": 20801,
      "l": "dos Santos Aveiro",
      "r": 93
    }
    required_prices = ['LCPrice','LCPrice2','LCPrice3']
    player_prices = {}
    temp_prices_list = []
    if (common_player_name):
        player_id = str(player.get('id'))
        url_of_specific_player_prices = f'{FUTBIN_PLAYER_PRICE_URL}{player_id}'
        prices_of_specific_player = json.loads(requests.get(url_of_specific_player_prices).content)
        for console in prices_of_specific_player[player_id]['prices']:
            for LCPrice in required_prices:
                temp_prices_list.append(prices_of_specific_player[player_id]['prices'][console][LCPrice])
            player_prices[console] = temp_prices_list
            temp_prices_list = []
        for (key, value) in player_prices.items():
            for price in value:
                if ',' in price:
                    player_prices[key] = price.replace(',', '')
                player_prices[key] = int(player_prices[key])
        print(player_prices)










