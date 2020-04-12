from consts import server_status_messages
from loops.main_search_loop import run_search_loop
from loops.pre_loop_actions import get_loop_item_for_search
from models.fab_loop import FabLoop
from search_filters.filtered_search import FilteredSearch
from utils.helper_functions import server_response


class PlayerLoop(FabLoop):
    def __init__(self, fab, configuration_data, items_with_filters):
        self.fab = fab
        self.configuration_data = configuration_data
        self.items_with_filters = items_with_filters

    def start_loop(self):
        player_to_search = get_loop_item_for_search(self.fab, self.items_with_filters)
        if player_to_search is None:
            return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)
        # enter_transfer_market(fab)
        FilteredSearch(self.fab.element_actions, player_to_search).set_custom_search_filteres()
        return run_search_loop(self.fab, self.configuration_data, player_to_search, self.items_with_filters)
