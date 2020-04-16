from consts import server_status_messages
from fab_loop.main_search_loop import run_search_loop
from fab_loop.pre_loop_actions import get_item_for_loop_search, execute_pre_run_actions
from search_filters.filter_setter import FilterSetter
from utils.helper_functions import server_response


def start_loop(fab, configuration, items):
    if not execute_pre_run_actions(fab):
        return server_response(msg=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)
    item_to_search = get_item_for_loop_search(fab, items)
    if item_to_search is None:
        return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)
    FilterSetter(fab.element_actions, item_to_search).set_search_filteres()
    return run_search_loop(fab, configuration, item_to_search, items)
