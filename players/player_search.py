from consts import elements
from items.item_search import get_next_item_to_search
from players.player_init_market_search import PlayerMarketSearch
from user_info.user_actions import update_coin_balance


def update_search_player_if_coin_balance_changed(fab, player_to_search, requested_players, real_prices):
    new_coin_balance = int(fab.element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    if new_coin_balance != fab.user.coin_balance:
        update_coin_balance(fab.user.email, fab.element_actions)
        player_to_search = get_next_item_to_search(fab.user.coin_balance, requested_players, real_prices)
        if player_to_search is not None:
            init_new_player_search(fab.element_actions, player_to_search)
    return player_to_search


def init_new_player_search(element_actions, player_to_search, price_to_search=None,filters=None):
    player_market_search = PlayerMarketSearch(element_actions)
    if not filters:
        if not price_to_search:
            price_to_search = str(player_to_search.get_max_buy_price())
        search_player_name = player_to_search.name
        player_market_search.init_market_search(search_player_name, price_to_search)
    else:
        print("implement her the filtered selection")
        pass


