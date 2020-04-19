import time

from consts import elements, server_status_messages
from consts.app import CURRENT_WORKING_DIR
from enums.actions_for_execution import ElementCallback
from items.next_item_to_search import update_search_item_if_coin_balance_changed
from models.price_evaluator import get_sell_price
from ea_account_info.ea_account_actions import update_earned_coins_in_fab, update_ea_account_total_runtime_db, update_ea_account_coins_earned_db
from utils.driver_functions import evaluate_driver_operation_time, close_driver
from utils.helper_functions import get_coin_balance_from_web_app, server_response
from utils.market import decrease_increase_min_price


def run_search_loop(fab, loop_configuration, item_to_search, requested_items):
    increase_min_price = True
    num_of_tries = 0
    if not fab.time_left_to_run:
        time_to_run_in_sec = loop_configuration["time"]
    else:
        time_to_run_in_sec = fab.time_left_to_run

    is_item_listed_after_buy = loop_configuration["autoList"]

    start = time.time()
    while True:
        num_of_tries = evaluate_driver_operation_time(fab, start, time_to_run_in_sec, num_of_tries)
        if num_of_tries is False: break
        ### search
        fab.element_actions.execute_element_action(elements.SEARCH_ITEM_BTN, ElementCallback.CLICK)
        ### buy
        time.sleep(0.5)

        current_budget = get_coin_balance_from_web_app(fab.element_actions)
        if current_budget is None:
            close_driver(fab.driver, fab.ea_account.email)
            return server_response(msg=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)

        # item_bought, bought_for = fab.item_actions.buy_item(current_budget)
        # if item_bought and bought_for:
        #     list_price = get_sell_price(item_to_search['marketPrice'])
        #     fab.driver.save_screenshot(f"{CURRENT_WORKING_DIR}\\screenshots\\bought for {bought_for}.png")
        #     print(f"bought for={bought_for}")
        #     update_earned_coins_in_fab(fab, list_price, bought_for)
        #     if is_item_listed_after_buy:
        #         pass
        #         # print(f"listed={list_price}")
        #         # self.item_actions.list_player(str(list_price))
        #     fab.element_actions.execute_element_action(elements.SEND_TO_TRANSFER_BTN, ElementCallback.CLICK)
        fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        item_to_search = update_search_item_if_coin_balance_changed(fab, item_to_search, requested_items)
        if item_to_search is None:
            return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)

        decrease_increase_min_price(fab.element_actions, increase_min_price)
        increase_min_price = not increase_min_price
        ### time check
        print(num_of_tries)

    update_ea_account_coins_earned_db(fab)
    update_ea_account_total_runtime_db(fab)
    return server_response(msg=server_status_messages.FAB_LOOP_FINISHED, code=200)
