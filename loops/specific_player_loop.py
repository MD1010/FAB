from consts import server_status_messages
from items.item_prices import get_or_find_item_prices
from loops.fab_loop import FabLoop
from loops.main_search_loop import start_search_loop
from loops.pre_loop_actions import execute_pre_run_actions, get_item_to_search_according_to_prices
from players.player_search import init_new_player_search
from utils.helper_functions import server_response

class SpecificPlayerLoop(FabLoop):
    def start_loop(self, fab, configuration_data, requested_players, user_prices):
        execute_pre_run_actions(fab)
        is_user_decides_prices = configuration_data["userDecidesPrices"]
        player_prices = get_or_find_item_prices(fab, is_user_decides_prices, requested_players, user_prices)
        if player_prices is None:
            return server_response(msg=server_status_messages.PRICES_FIELD_WAS_NOT_SPECIFIED, code=503)
        player_to_search = get_item_to_search_according_to_prices(fab, requested_players, player_prices)
        if player_to_search is None:
            return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)
        # enter_transfer_market(fab)
        init_new_player_search(fab.element_actions, player_to_search)
        return start_search_loop(fab, configuration_data, player_to_search, requested_players, player_prices)
