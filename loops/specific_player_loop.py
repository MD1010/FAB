from consts import server_status_messages
from items.item_prices import get_or_find_item_prices
from loops.fab_loop import FabLoop
from loops.main_search_loop import run_search_loop
from loops.pre_loop_actions import execute_pre_run_actions, get_item_to_search_according_to_prices

from search_filters.filtered_search_by_name import NameFilteredSearch
from utils.helper_functions import server_response


class NameFilteredPlayerLoop(FabLoop):
    def start_loop(self, fab, configuration_data, requested_players, user_items_with_prices, filters=None):
        execute_pre_run_actions(fab)
        is_user_decides_prices = configuration_data["userDecidesPrices"]
        requested_players = get_or_find_item_prices(fab, is_user_decides_prices, requested_players, user_items_with_prices)
        if requested_players is None:
            return server_response(msg=server_status_messages.PRICES_FIELD_WAS_NOT_SPECIFIED, code=503)
        player_to_search = get_item_to_search_according_to_prices(fab.user.coin_balance, requested_players)
        if player_to_search is None:
            return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)
        # enter_transfer_market(fab)
        NameFilteredSearch().set_search_filteres(fab.element_actions, player_to_search)
        return run_search_loop(fab, configuration_data, player_to_search, requested_players)
