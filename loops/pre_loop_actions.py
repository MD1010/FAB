from items.next_item_to_search import get_next_item_to_search
from user_info.user_actions import update_coin_balance
from utils.helper_functions import server_response
from utils.market import enter_transfer_market


def execute_pre_run_actions(fab):
    update_coin_balance(fab.user.email, fab.element_actions)
    fab.element_actions.wait_for_page_to_load()
    # get updated rt_prices
    enter_transfer_market(fab.element_actions)


def get_item_to_search_according_to_prices(user_coin_balance, requested_items):
    item_to_search = get_next_item_to_search(user_coin_balance, requested_items)
    if item_to_search is None:
        return None
    return item_to_search
