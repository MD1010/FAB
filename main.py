from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

import time
import os.path
from auth.login import set_auth_status, check_auth_status, login_with_cookies, login_first_time, remember_logged_in_user, wait_for_code
from players.player_buy import decrease_increase_min_price
from scripts import selenium
from consts import app, elements, server_status_messages
from helper_functions import loadCookiesFile, saveToCookiesFile
from players.players_actions import PlayerActions
from elements.elements_manager import ElementCallback, ElementActions, initialize_element_actions
from seleniumDriver.driver import initialize_driver
from players.player_buy import get_current_player_min_price

from players import player
def run_loop(self,time_to_run_in_sec):
    increase_min_price = True
    start = time.time()
    while True:
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        # time.sleep(1)

        player_bought = self.playerActions.buy_player()
        #player_bought = None
        if player_bought:
            self.playerActions.list_player("500")
        else:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price
        curr_time = time.time()
        if curr_time - start > time_to_run_in_sec :
            break


class Fab:
    def __init__(self):
        self.is_authenticated = False
        self.driver = None
        self.statusCode = ''
        self.element_actions = None
        self.playerActions = None

    def start_login(self, email, password):
        try:
            initialize_driver(self)
            initialize_element_actions(self)
            if os.path.isfile(app.COOKIES_FILE_NAME):
                login_with_cookies(self, password)

            # cookies file was not found - log in the first time
            else:
                login_first_time(self, email, password)
                # can be screwed here, may send bad status here..
                wait_for_code(self)
                remember_logged_in_user(self)
                set_auth_status(self, True)
            return server_status_messages.SUCCESS_AUTH, 200

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return server_status_messages.FAILED_AUTH, 401

    @check_auth_status
    def start_loop(self,time_to_run_in_sec):
        try:
            self.playerActions = PlayerActions(self.driver)
            self.element_actions.wait_for_page_to_load()
            self.element_actions.remove_unexpected_popups()
            current_player_updated_price = get_current_player_min_price("Ronaldo Luís","Nazário de Lima","95","Ronaldo")
            self.playerActions.init_search_player_info("tallo", "600")
            run_loop(self,time_to_run_in_sec)
            return server_status_messages.FAB_LOOP_FINISHED, 200

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return server_status_messages.FAB_LOOP_FAILED, 404

    def set_status_code(self, code):
        self.statusCode = code
        return server_status_messages.STATUS_CODE_SET_CORRECTLY, 200
