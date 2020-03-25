import json

import requests
from selenium.common.exceptions import TimeoutException, WebDriverException

import time
import os.path
from auth.login import set_auth_status, check_auth_status, login_with_cookies, login_first_time, remember_logged_in_user, wait_for_code
from consts.app import AMOUNT_OF_SEARCHES_BEFORE_SLEEP, SLEEP_MID_OPERATION_DURATION, FUTHEAD_PLAYER, CHROME_DRIVER_PROCESS_NAME
from players.player_search import decrease_increase_min_price, get_player_to_search, init_new_search, enter_transfer_market, get_all_players_RT_prices, \
    get_all_players_cards, update_search_player_if_coin_balance_changed
from consts import app, elements, server_status_messages
from players.players_actions import PlayerActions

from elements.elements_manager import ElementCallback, initialize_element_actions
from driver import initialize_driver, DriverState, restart_driver_when_crashed, evaluate_driver_operation_time
from server_status import ServerStatus
from user_info import user
from user_info.user import get_coin_balance, get_user_platform

import psutil


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
        ### search
        player_to_search = update_search_player_if_coin_balance_changed(self,player_to_search,requested_players,real_prices)
        if player_to_search is None:
            return ServerStatus(server_status_messages.NO_BUDGET_LEFT, 503).jsonify()

        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)

        ### buy
        player_bought = self.player_actions.buy_player()
        if player_bought:
            player_to_search.get_sell_price()
            list_price = player_to_search.sell_price
            print(f"listed={list_price}")
            self.player_actions.list_player(str(list_price))

        self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)
        if player_bought: time.sleep(1)

        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price

        ### time check
        num_of_tries = evaluate_driver_operation_time(self,start,time_to_run_in_sec,num_of_tries)
        if num_of_tries is False: break
        print(num_of_tries)
    return ServerStatus(server_status_messages.FAB_LOOP_FINISHED, 200).jsonify()


def initialize_user_details(self,email, password):
    self.connected_user_details["email"] = email
    self.connected_user_details["password"] = password

class Fab:
    def __init__(self):
        self.is_authenticated = False
        self.driver = None
        self.statusCode = ''
        self.element_actions = None
        self.player_actions = None
        self.driver_state = DriverState.OFF
        self.connected_user_details = {}
        self.time_left_to_run = 0

    def start_login(self, email, password):
        if email is None or password is None:
            return ServerStatus(server_status_messages.BAD_REQUEST, 400).jsonify()
        try:
            initialize_user_details(self,email,password)
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
            print("restarting FAB...")
            restart_driver_when_crashed(self,requested_players)