from items.items_priorities import get_item_to_search_according_to_prices, set_items_priorities
from models.price_evaluator import check_items_market_prices
from user_info.user_actions import update_coin_balance
from utils.market import enter_transfer_market


def execute_pre_run_actions(fab):
    update_coin_balance(fab.user.email, fab.element_actions)
    fab.element_actions.wait_for_page_to_load()
    # get updated prices
    enter_transfer_market(fab.element_actions)


def get_loop_item_for_search(fab, items):
    execute_pre_run_actions(fab)
    check_items_market_prices(fab, items)
    set_items_priorities(items,fab.user.coin_balance)
    item_to_search = get_item_to_search_according_to_prices(items)
    return item_to_search
