from items.items_priorities import get_item_to_search_according_to_prices, set_items_priorities
from models.price_evaluator import check_items_market_prices
from user_info.user_actions import update_coin_balance
from utils.driver_functions import close_driver
from utils.helper_functions import get_coin_balance_from_web_app
from utils.market import enter_transfer_market


def execute_pre_run_actions(fab):
    update_coin_balance(fab.user.email, fab.element_actions)
    fab.element_actions.wait_for_page_to_load()
    # get updated prices
    enter_transfer_market(fab.element_actions)
    #chech if coin balance is available - if not then there is a problem with the web app
    if get_coin_balance_from_web_app(fab.element_actions) is None:
        close_driver(fab.driver, fab.user.email)
        return False
    return True


def get_item_for_loop_search(fab, items):
    check_items_market_prices(fab, items)
    set_items_priorities(items,fab.user.coin_balance)
    item_to_search = get_item_to_search_according_to_prices(items)
    return item_to_search
