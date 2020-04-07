import time

from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib3.exceptions import MaxRetryError

from auth.auth_status import set_auth_status
from consts import server_status_messages, elements
from consts.app import CURRENT_WORKING_DIR, MAX_DRIVER_CRASHES_COUNT
from elements.actions_for_execution import ElementCallback
from players.player_min_prices import get_all_players_RT_prices
from players.player_search import get_player_to_search, init_new_search, update_search_player_if_coin_balance_changed
from user_info.user import update_coin_balance
from utils.driver import evaluate_driver_operation_time, close_driver, initialize_time_left
from utils.helper_functions import server_response
from utils.market import enter_transfer_market, decrease_increase_min_price


def run_loop(fab, time_to_run_in_sec, requested_players):
    increase_min_price = True
    num_of_tries = 0

    update_coin_balance(fab.user.email, fab.element_actions)

    fab.element_actions.wait_for_page_to_load()
    # get updated prices
    enter_transfer_market(fab)
    real_prices = get_all_players_RT_prices(fab, requested_players)
    player_to_search = get_player_to_search(fab, requested_players, real_prices)
    if player_to_search is None:
        return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)

    # enter_transfer_market(fab)
    init_new_search(fab, player_to_search)

    start = time.time()
    while True:
        num_of_tries = evaluate_driver_operation_time(fab, start, time_to_run_in_sec, num_of_tries)
        if num_of_tries is False: break
        ### search
        fab.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        ### buy
        time.sleep(0.5)

        player_bought, bought_for = fab.player_actions.buy_player()
        if player_bought and bought_for:
            # {CURRENT_WORKING_DIR}\\screenshots\\
            list_price = player_to_search.get_sell_price()
            fab.driver.save_screenshot(f"{CURRENT_WORKING_DIR}\\screenshots\\min price {list_price},bought for {bought_for}.png")
            print(f"bought for={bought_for}")
            # print(f"listed={list_price}")
            # self.player_actions.list_player(str(list_price))
            fab.element_actions.execute_element_action(elements.SEND_TO_TRANSFER_BTN, ElementCallback.CLICK)
            print("sent to transfer list")
        fab.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        player_to_search = update_search_player_if_coin_balance_changed(fab, player_to_search, requested_players, real_prices)
        if player_to_search is None:
            return server_response(msg=server_status_messages.NO_BUDGET_LEFT, code=503)

        decrease_increase_min_price(fab, increase_min_price)
        increase_min_price = not increase_min_price

        ### time check
        print(num_of_tries)
    return server_response(msg=server_status_messages.FAB_LOOP_FINISHED, code=200)


def start_fab(fab, time_to_run_in_sec, requested_players):
    if time_to_run_in_sec is None:
        return server_response(msg=server_status_messages.BAD_REQUEST, code=400)
    try:
        run_loop_response = run_loop(fab, time_to_run_in_sec, requested_players)

        set_auth_status(fab.user.email, False)
        close_driver(fab.driver, fab.user.email)
        return run_loop_response

    except MaxRetryError as e:
        return server_response(msg=server_status_messages.DRIVER_OFF, code=503)

    except (WebDriverException, TimeoutException) as e:
        print(f"Oops :( Something went wrong.. {e.msg}")
        print("restarting FAB...")
        fab.driver_crashes += 1
        if fab.driver_crashes == MAX_DRIVER_CRASHES_COUNT:
            close_driver(fab.driver, fab.user.email)
            return server_response(msg=server_status_messages.DRIVER_CRASHED_TOO_MANY_TIMES, code=503)
        # only if it has not started yet
        if fab.time_left_to_run == 0:
            initialize_time_left(fab, time_to_run_in_sec)
        return start_fab(fab, time_to_run_in_sec, requested_players)
