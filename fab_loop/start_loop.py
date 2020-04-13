from consts import server_status_messages
from fab_loop.main_search_loop import run_search_loop
from fab_loop.pre_loop_actions import get_item_for_loop_search
from search_filters.filter_setter import FilterSetter
from utils.helper_functions import server_response


def start_loop(fab, configuration, items):
    item_to_search = get_item_for_loop_search(fab, items)
    if item_to_search is None:
        return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)
    # enter_transfer_market(fab)
    FilterSetter(fab.element_actions, item_to_search).set_custom_search_filteres()
    return run_search_loop(fab, configuration, item_to_search, items)
