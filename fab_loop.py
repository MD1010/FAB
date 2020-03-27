import time

from consts import server_status_messages, elements
from driver import evaluate_driver_operation_time
from elements.models.actions_for_execution import ElementCallback
from players.player_search import enter_transfer_market, get_all_players_RT_prices, get_player_to_search, init_new_search, update_search_player_if_coin_balance_changed, \
    decrease_increase_min_price
from server_status import ServerStatus
from user_info import user
from user_info.user import get_coin_balance, get_user_platform


def run_loop(self, time_to_run_in_sec, requested_players):
    increase_min_price = True
    num_of_tries = 0
    user.coin_balance = get_coin_balance(self)
    user.user_platform = get_user_platform(self)
    self.element_actions.wait_for_page_to_load()
    # get updated prices
    enter_transfer_market(self)
    real_prices = get_all_players_RT_prices(self, requested_players)
    player_to_search = get_player_to_search(requested_players, real_prices)
    if player_to_search is None:
        return ServerStatus(server_status_messages.NO_BUDGET_LEFT, 503).jsonify()
    enter_transfer_market(self)
    init_new_search(self, player_to_search)

    start = time.time()
    while True:
        num_of_tries = evaluate_driver_operation_time(self, start, time_to_run_in_sec, num_of_tries)
        if num_of_tries is False: break
        ### search
        player_to_search = update_search_player_if_coin_balance_changed(self, player_to_search, requested_players, real_prices)
        if player_to_search is None:
            return ServerStatus(server_status_messages.NO_BUDGET_LEFT, 503).jsonify()

        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)

        ### buy
        time.sleep(0.5)

        player_bought, bought_for = self.player_actions.buy_player()
        if player_bought and bought_for:
            list_price = player_to_search.get_sell_price()
            print(f"bought for={bought_for}")
            # print(f"listed={list_price}")
            # self.player_actions.list_player(str(list_price))
            self.element_actions.execute_element_action(elements.SEND_TO_TRANSFER_BTN,ElementCallback.CLICK)
            print("sent to tr")
            time.sleep(2)
        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price

        ### time check
        print(num_of_tries)


    return ServerStatus(server_status_messages.FAB_LOOP_FINISHED, 200).jsonify()
