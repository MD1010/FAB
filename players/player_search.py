from multiprocessing.pool import ThreadPool

from consts import elements
from players.player import Player
from players.players_objects import build_player_objects, get_cards_from_the_same_player
from user_info.user import update_coin_balance
from utils import db


def _get_player_full_futhead_data(contain_searched_term_players):
    if len(contain_searched_term_players) == 0: return []
    player_thread_pool = ThreadPool(len(contain_searched_term_players))
    players_imap_iterator = player_thread_pool.imap(get_cards_from_the_same_player, contain_searched_term_players)
    player_thread_pool.close()
    player_thread_pool.join()
    result = []
    for _, player_record in players_imap_iterator._items:
        if len(player_record) > 0:
            for player_data in player_record:
                player_card = Player(player_data.id, player_data.name, player_data.rating, player_data.revision, player_data.nation, player_data.position,
                                     player_data.club)
                result.append(player_card)
    return result


def update_search_player_if_coin_balance_changed(fab, player_to_search, requested_players, real_prices):
    new_coin_balance = int(fab.element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    if new_coin_balance != fab.user.coin_balance:
        update_coin_balance(fab)
        player_to_search = get_player_to_search(fab, requested_players, real_prices)
        if player_to_search is not None:
            init_new_search(fab, player_to_search)
    return player_to_search


def init_new_search(fab, player_to_search):
    search_max_price = str(player_to_search.get_max_buy_price())
    search_player_name = player_to_search.name
    fab.player_actions.init_search_player_info(search_player_name, search_max_price)


def get_player_to_search(fab, requested_players, real_prices):
    requested_players = list(build_player_objects(fab, requested_players, real_prices))
    sorted_by_profit = sorted(requested_players, key=lambda player: player.profit, reverse=True)
    most_profitable_player = sorted_by_profit[0]
    # if all the players are above the budget
    if most_profitable_player.profit == 0:
        return None
    else:
        return sorted_by_profit[0]


def get_all_players_cards(searched_player_name_string):
    contain_searched_term_players = list(
        db.players_collection.find({"name": {'$regex': f".*{searched_player_name_string}.*", '$options': 'i'}}).limit(20).sort('rating', -1))
    unsorted_result = _get_player_full_futhead_data(contain_searched_term_players)
    sorted_by_rating_result = sorted(unsorted_result, key=lambda player: player.rating, reverse=True)
    return sorted_by_rating_result
