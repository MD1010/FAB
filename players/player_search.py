import concurrent
import multiprocessing
from multiprocessing import Process
from concurrent import futures
from multiprocessing.pool import ThreadPool

import pymongo
from bson.son import SON
import db
from consts import elements
from elements.elements_manager import ElementCallback
import requests
import json

from players.models.player import Player
from consts.app import FUTBIN_PLAYER_PRICE_URL, MAX_PRICE, SANE_PRICE_RATIO, FUTHEAD_PLAYER, MIN_PRICE
from user_info import user


def enter_transfer_market(self):
    # click on TRANSFERS
    self.element_actions.execute_element_action(elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)
    # click on search on transfer market
    self.element_actions.execute_element_action(elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)


def get_next_player_search(self, player_to_search):
    search_max_price = str(player_to_search.max_buy_price)
    search_player_name = player_to_search.name
    return self.player_actions.init_search_player_info(search_player_name, search_max_price)


def decrease_increase_min_price(self, increase_price):
    # check if price can be decreased
    decrease_btn = self.element_actions.get_element(elements.DECREASE_MIN_PRICE_BTN)
    can_be_decreased = decrease_btn.is_enabled() if decrease_btn else False
    max_bin_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value") if max_bin_price else str(MIN_PRICE)
    can_be_increased = True if max_bin != str(MIN_PRICE) else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        self.element_actions.execute_element_action(elements.INCREASE_MIN_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        self.element_actions.execute_element_action(elements.DECREASE_MIN_PRICE_BTN, ElementCallback.CLICK)


def get_player_to_search(requested_players, real_prices):
    requested_players = list(_build_player_objects(requested_players, real_prices))
    sorted_by_profit = sorted(requested_players, key=lambda player: player.profit, reverse=True)
    most_profitable_player = sorted_by_profit[0]
    # if all the players are above the budget
    if most_profitable_player.profit == 0:
        return None
    else:
        return sorted_by_profit[0]


def get_approximate_min_price(full_name, revision_type):
    player_prices = []
    required_prices = ['LCPrice', 'LCPrice2', 'LCPrice3']

    player_id = _get_player_attribute_from_json(full_name, revision_type, 'def_id')

    url_of_specific_player_prices = f'{FUTBIN_PLAYER_PRICE_URL}{player_id}'
    prices_of_specific_player = json.loads(requests.get(url_of_specific_player_prices).content)

    for LCPrice in required_prices:
        player_prices.append(prices_of_specific_player[player_id]['prices'][user.user_platform][LCPrice])

    for price_index in range(len(player_prices)):
        if ',' in str(player_prices[price_index]):
            player_prices[price_index] = player_prices[price_index].replace(',', '')
    price_after_sanity = _min_price_after_prices_sanity_check(player_prices)
    return price_after_sanity


def _get_player_attribute_from_json(full_name, revision_type, player_attribute):
    futhead_url_player_data = f'{FUTHEAD_PLAYER}{full_name}'
    details_of_specific_player = json.loads(requests.get(futhead_url_player_data).content)
    for element in details_of_specific_player:
        if element.get('full_name') == full_name and element.get('revision_type') == revision_type:
            return str(element.get(player_attribute))


def get_all_players_RT_prices(self, required_players):
    RT_prices = []
    for player in required_players:
        player_name = player["name"]
        player_revision = player["revision"]
        real_price = self.player_actions.check_player_RT_price(player_name, player_revision)
        RT_prices.append({player_name: real_price})
    return RT_prices



def get_all_players_cards(searched_player_name_string):
    contain_searched_term_players = list(db.players_collection.find({"name" : {'$regex' : f".*{searched_player_name_string}.*",'$options': 'i'}}).limit(20).sort('rating', -1))
    unsorted_result = _get_player_full_futhead_data(contain_searched_term_players)
    sorted_by_rating_result = sorted(unsorted_result, key=lambda player: player.rating, reverse=True)
    return sorted_by_rating_result


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


def _build_player_objects(requested_players, real_prices):
    result = []
    for player in requested_players:
        player_name = player["name"]
        rating = player["rating"]
        specific_card_id = player["def_id"]
        revision = player["revision_type"]
        name = player["full_name"]
        nation = player["nation_name"]
        position = player["position"]
        club = player["club_name"]

        player_market_price = 0
        for price_obj in real_prices:
            for name in price_obj.keys():
                if name == player_name:
                    player_market_price = price_obj[player_name]
                    break
        player_obj = Player(specific_card_id, player_name, rating, revision, nation, position, club)
        player_obj.set_market_price(player_market_price)
        player_obj.calculate_max_buy_price()
        player_obj.calculate_profit()
        result.append(player_obj)
    return result


def _build_full_player_data_obj(ea_player_data):
    # if ea_player_data.get("c") is not None:
    #     player_full_name = ea_player_data.get("c")
    # else:
    #     player_full_name = ea_player_data.get("f") + " " + ea_player_data.get("l")
    player_full_name = ea_player_data.get("name")
    player_id = ea_player_data.get("id")
    # go to futhead to find all cards of that player
    futhead_url_player_data = f'{FUTHEAD_PLAYER}{player_full_name}'
    details_of_specific_player = json.loads(requests.get(futhead_url_player_data).content)

    cards_from_the_same_id = []
    for player_in_json_futhead in details_of_specific_player:
        if player_in_json_futhead["player_id"] == player_id:
            rating = player_in_json_futhead["rating"]
            specific_card_id = player_in_json_futhead["def_id"]
            revision = player_in_json_futhead["revision_type"]
            name = player_in_json_futhead["full_name"]
            nation = player_in_json_futhead["nation_name"]
            position = player_in_json_futhead["position"]
            club = player_in_json_futhead["club_name"]
            cards_from_the_same_id.append(Player(specific_card_id, name, rating, revision, nation, position, club))
    return cards_from_the_same_id


def _get_player_full_futhead_data(contain_searched_term_players):
    if len(contain_searched_term_players) == 0: return []
    player_thread_pool = ThreadPool(len(contain_searched_term_players))
    players_imap_iterator = player_thread_pool.imap(_build_full_player_data_obj, contain_searched_term_players)
    player_thread_pool.close()
    player_thread_pool.join()
    result = []
    for _, player_record in players_imap_iterator._items:
        if len(player_record) > 0:
            for player_data in player_record:
                # id, name, rating, revision, nation, position, club = player_data.values()
                player_card = Player(player_data.id, player_data.name, player_data.rating, player_data.revision, player_data.nation, player_data.position,
                                     player_data.club)
                result.append(player_card)
    return result
