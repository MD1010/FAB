from consts import server_status_messages
from loops.fab_loop import FabLoop
from loops.main_search_loop import run_search_loop
from loops.pre_loop_actions import get_loop_item_for_search

from search_filters.filtered_search_by_name import NameFilteredSearch
from utils.helper_functions import server_response


class NameFilteredPlayerLoop(FabLoop):
    def start_loop(self, fab, configuration_data, requested_players, filters=None):
        player_to_search = get_loop_item_for_search(fab, requested_players)
        if player_to_search is None:
            return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)
        # enter_transfer_market(fab)
        NameFilteredSearch().set_search_filteres(fab.element_actions, player_to_search)
        return run_search_loop(fab, configuration_data, player_to_search, requested_players)
