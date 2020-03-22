import json

import requests
from selenium.common.exceptions import TimeoutException, WebDriverException

import time
import os.path
from auth.login import set_auth_status, check_auth_status, login_with_cookies, login_first_time, remember_logged_in_user, wait_for_code
from consts.app import AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION, FUTHEAD_PLAYER
from helper_functions import saveToCookiesFile
from players.models.player import Player
from players.player_search import decrease_increase_min_price, get_player_to_search, get_next_player_search, enter_transfer_market, get_all_players_RT_prices, \
    get_all_players_cards
from consts import app, elements, server_status_messages
from players.players_actions import PlayerActions

from elements.elements_manager import ElementCallback, initialize_element_actions
from driver import initialize_driver, DriverState
from server_status import ServerStatus
from user_info import user
from user_info.user import get_coin_balance, get_user_platform


def run_loop(self, time_to_run_in_sec, requested_players):
    increase_min_price = True
    num_of_tries = 0
    user.coin_balance = get_coin_balance(self)
    user.user_platform = get_user_platform(self)
    # get updated prices
    enter_transfer_market(self)
    real_prices = get_all_players_RT_prices(self, requested_players)
    player_to_search = get_player_to_search(requested_players, real_prices)
    if player_to_search is None:
        return ServerStatus(server_status_messages.NO_BUDGET_LEFT, 503).jsonify()
    enter_transfer_market(self)
    time.sleep(1)
    found_next_player = get_next_player_search(self, player_to_search)
    if found_next_player is False:
        return ServerStatus(server_status_messages.SEARCH_PROBLEM, 503).jsonify()

    start = time.time()
    while True:
        current_coin_balance = get_coin_balance(self)
        if user.coin_balance != current_coin_balance:
            user.coin_balance = current_coin_balance
            # real_prices = get_all_players_RT_prices(self, requested_players)
            player_to_search = get_player_to_search(requested_players, real_prices)
            if player_to_search is None:
                return ServerStatus(server_status_messages.NO_BUDGET_LEFT, 503).jsonify()
            found_next_player = get_next_player_search(self, player_to_search)
            if found_next_player is False:
                return ServerStatus(server_status_messages.SEARCH_PROBLEM, 503).jsonify()

        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)

        # give time for the elements in the page to render - if remove stale exception
        time.sleep(1)
        # player_bought = self.player_actions.buy_player()
        print(player_to_search.max_buy_price)
        player_bought = None

        if player_bought:
            list_price = player_to_search.sell_price
            self.player_actions.list_player(str(list_price))

        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        # else:
        #     self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price
        curr_time = time.time()
        if curr_time - start > time_to_run_in_sec:
            break
        num_of_tries += 1
        if num_of_tries % AMOUNT_OF_SEARCHES_BEFORE_SLEEP == 0:
            time.sleep(SLEEP_MID_OPERATION_DURATION)
        time.sleep(1.5)
    print(num_of_tries)
    return ServerStatus(server_status_messages.FAB_LOOP_FINISHED, 200).jsonify()


class Fab:
    def __init__(self):
        self.is_authenticated = False
        self.driver = None
        self.statusCode = ''
        self.element_actions = None
        self.player_actions = None
        self.driver_state = DriverState.OFF

    def start_login(self, email, password):
        if email is None or password is None:
            return ServerStatus(server_status_messages.BAD_REQUEST, 400).jsonify()
        try:
            initialize_driver(self)
            initialize_element_actions(self)
            if os.path.isfile(app.COOKIES_FILE_NAME):
                if not login_with_cookies(self, password):
                    return ServerStatus(server_status_messages.FAILED_AUTH, 401).jsonify()

            # cookies file was not found - log in the first time
            else:
                if not login_first_time(self, email, password):
                    return ServerStatus(server_status_messages.FAILED_AUTH, 401).jsonify()
                # can be screwed here, may send bad status here..
                tries = 3
                while tries > 0:
                    if not wait_for_code(self):
                        pass
                    tries -= 1
                if tries == 0:
                    return ServerStatus(server_status_messages.LIMIT_TRIES, 401).jsonify()
                remember_logged_in_user(self)
                set_auth_status(self, True)
            return ServerStatus(server_status_messages.SUCCESS_AUTH, 200).jsonify()

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return ServerStatus(server_status_messages.FAILED_AUTH, 401).jsonify()

    @check_auth_status
    def start_loop(self, time_to_run_in_sec, requested_players):
        if time_to_run_in_sec is None:
            return ServerStatus(server_status_messages.BAD_REQUEST, 400).jsonify()
        try:
            self.player_actions = PlayerActions(self.driver)
            self.element_actions.wait_for_page_to_load()
            self.element_actions.remove_unexpected_popups()
            return run_loop(self, time_to_run_in_sec, requested_players)

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return ServerStatus(server_status_messages.FAB_LOOP_FAILED, 503).jsonify()

    def set_status_code(self, code):
        self.statusCode = code
        return ServerStatus(server_status_messages.STATUS_CODE_SET_CORRECTLY, 200).jsonify()

    def close_driver(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver_state = DriverState.OFF
            return ServerStatus(server_status_messages.FAB_DRIVER_CLOSE_SUCCESS, 200).jsonify()
        else:
            return ServerStatus(server_status_messages.FAB_DRIVER_CLOSE_FAIL, 503).jsonify()
