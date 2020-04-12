from items.item_data import build_search_option_objects_from_dict
from items.item_prices import get_all_items_RT_prices
from items.next_item_to_search import get_next_option_to_search
from user_info.user_actions import update_coin_balance
from utils.market import enter_transfer_market


def execute_pre_run_actions(fab):
    update_coin_balance(fab.user.email, fab.element_actions)
    fab.element_actions.wait_for_page_to_load()
    # get updated prices
    enter_transfer_market(fab.element_actions)


def get_item_to_search_according_to_prices(user_coin_balance, search_options):
    item_to_search = get_next_option_to_search(user_coin_balance, search_options)
    return item_to_search


def get_loop_item_for_search(fab, search_options):
    execute_pre_run_actions(fab)
    search_options = build_search_option_objects_from_dict(search_options)
    search_options = get_all_items_RT_prices(fab, search_options)
    item_to_search = get_item_to_search_according_to_prices(fab.user.coin_balance, search_options)
    return item_to_search
