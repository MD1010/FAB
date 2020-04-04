import time

from flask import jsonify
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib3.exceptions import MaxRetryError

from auth.login import check_auth_status
from consts import server_status_messages, elements
from elements.actions_for_execution import ElementCallback
from players.player_min_prices import get_all_players_RT_prices
from players.player_search import get_player_to_search, init_new_search, update_search_player_if_coin_balance_changed
from players.players_actions import PlayerActions
from user_info.user import get_coin_balance, get_user_platform, get_user_name
from utils.driver import evaluate_driver_operation_time, DriverState, check_if_web_app_is_available, close_driver, initialize_time_left, restart_driver_when_crashed
from utils.market import enter_transfer_market, decrease_increase_min_price


def run_loop(self, time_to_run_in_sec, requested_players):
    increase_min_price = True
    num_of_tries = 0
    # todo: pay attention that user.coin_balance was removed and now it will be 0 thus it will exit the driver
    coin_balance = get_coin_balance(self)
    user_platform = get_user_platform(self)
    user_name = get_user_name(self)

    self.element_actions.wait_for_page_to_load()
    # get updated prices
    enter_transfer_market(self)
    real_prices = get_all_players_RT_prices(self, requested_players)
    player_to_search = get_player_to_search(requested_players, real_prices)
    if player_to_search is None:
        return jsonify(msg=server_status_messages.NO_BUDGET_LEFT, code=503)

    enter_transfer_market(self)
    init_new_search(self, player_to_search)

    start = time.time()
    while self.driver_state == DriverState.ON:
        num_of_tries = evaluate_driver_operation_time(self, start, time_to_run_in_sec, num_of_tries)
        if num_of_tries is False: break
        ### search
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        ### buy
        time.sleep(0.5)

        player_bought, bought_for = self.player_actions.buy_player()
        if player_bought and bought_for:
            # {CURRENT_WORKING_DIR}\\screenshots\\
            list_price = player_to_search.get_sell_price()
            self.driver.save_screenshot(f"min price {list_price},bought for {bought_for}.png")
            print(f"bought for={bought_for}")
            # print(f"listed={list_price}")
            # self.player_actions.list_player(str(list_price))
            self.element_actions.execute_element_action(elements.SEND_TO_TRANSFER_BTN, ElementCallback.CLICK)
            print("sent to transfer list")
        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        player_to_search = update_search_player_if_coin_balance_changed(self, player_to_search, requested_players, real_prices)
        if player_to_search is None:
            return jsonify(msg=server_status_messages.NO_BUDGET_LEFT, code=503)

        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price

        ### time check
        print(num_of_tries)
    return jsonify(msg=server_status_messages.FAB_LOOP_FINISHED, code=200)


@check_auth_status
def start_fab(self, time_to_run_in_sec, requested_players):
    if time_to_run_in_sec is None:
        return jsonify(msg=server_status_messages.BAD_REQUEST, code=400)
    try:
        self.player_actions = PlayerActions(self.driver)
        self.element_actions.wait_for_page_to_load()

        if not check_if_web_app_is_available(self):
            run_loop_response = jsonify(msg=server_status_messages.WEB_APP_NOT_AVAILABLE, code=503)
        else:
            self.element_actions.remove_unexpected_popups()
            run_loop_response = run_loop(self, time_to_run_in_sec, requested_players)

        set_auth_status(self, False)
        close_driver(self)
        return run_loop_response

    except MaxRetryError as e:
        return jsonify(msg=server_status_messages.DRIVER_OFF, code=503)

    except (WebDriverException, TimeoutException) as e:
        print(f"Oops :( Something went wrong.. {e.msg}")
        print("restarting FAB...")
        # only if it has not started yet
        if self.time_left_to_run == 0:
            initialize_time_left(self, time_to_run_in_sec)
        if self.driver_state == DriverState.ON:
            return restart_driver_when_crashed(self, requested_players)
