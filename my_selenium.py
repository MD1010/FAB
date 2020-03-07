from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

import time
import os.path

from functools import wraps

import selenium_scripts
import constants
import elements
from helper_functions import loadCookiesFile, saveToCookiesFile
from players_actions import PlayerActions
from elements_manager import ElementCallback, ElementActions, ElementPathBy
import server_status_messages


def check_auth_status(func):
    @wraps(func)
    def determine_if_func_should_run(self):
        if self.is_authenticated:
            return func(self)
        else:
            return server_status_messages.FAILED_AUTH, 401

    return determine_if_func_should_run


def set_auth_status(self, is_auth):
    self.is_authenticated = is_auth


def set_status_code(self, code):
    self.statusCode = code
    return server_status_messages.STATUS_CODE_SET_CORRECTLY, 200


def initialize_driver(self):
    self.driver = webdriver.Chrome(ChromeDriverManager().install())
    self.driver.get(constants.WEB_APP_URL)
    # self.driver.find_element_by_xpath().


def initialize_element_actions(self):
    self.element_actions = ElementActions(self.driver)


def login_with_cookies(self, password):
    self.driver.delete_all_cookies()
    cookies = loadCookiesFile(constants.COOKIES_FILE_NAME)
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        self.driver.add_cookie(cookie)
    self.driver.get(constants.WEB_APP_URL)

    self.element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)
    # Entering password left, and you are in!
    self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    set_auth_status(self, True)


def login_first_time(self, email, password):
    self.driver.get(constants.SIGN_IN_URL)
    self.element_actions.execute_element_action(elements.EMAIL_FIELD, ElementCallback.SEND_KEYS, email)
    self.element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
    # check the SMS option
    self.element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
    # send the sms verfication
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)


def wait_for_code(self):
    while self.statusCode is '':
        pass
    # What happens if the user is stupid enough to type the wrong code ? ? ?
    # status code is set
    self.element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS, self.statusCode)
    self.element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)


def remember_logged_in_user(self):
    eaCookies = self.driver.get_cookies()
    self.driver.get(constants.SIGN_IN_URL)
    signInCookies = self.driver.get_cookies()

    for cookie in signInCookies:
        if 'expiry' in cookie:
            del cookie['expiry']
        if cookie not in eaCookies:
            eaCookies.append(cookie)
    # takes 10-15 secs
    saveToCookiesFile(eaCookies, constants.COOKIES_FILE_NAME)
    self.driver.back()


def remove_unexpected_popups(self):
    popup = self.element_actions.get_clickable_element(elements.VIEW_MODAL_CONTAINER)
    if popup:
        self.driver.execute_script(selenium_scripts.REMOVE_ELEMENT, popup)


def decrease_increase_min_price(self, increase_price):
    # check if price can be decreased
    el = self.element_actions.get_clickable_element(elements.DECREASE_PRICE_BTN)
    can_be_decreased = el.is_enabled()
    max_bin_price = self.element_actions.get_clickable_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value")
    can_be_increased = True if max_bin != "200" else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        self.element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        self.element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)


def run_loop(self):
    loop_counter = 1
    increase_min_price = True
    while loop_counter < 10:
        self.element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
        # time.sleep(1)

        # player_bought = self.playerActions.buy_player()
        player_bought = None
        if player_bought:
            self.playerActions.list_player("500")
        else:
            self.element_actions.execute_element_action(elements.NAVIGATE_BACK, ElementCallback.CLICK)

        decrease_increase_min_price(self, increase_min_price)
        increase_min_price = not increase_min_price
        # if price is 200 not needed

        # if loop_counter % 2 == 1:
        #     self.element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
        # else:
        #     self.element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)
        loop_counter += 1


class FabDriver:
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
            if os.path.isfile(constants.COOKIES_FILE_NAME):
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
    def start_loop(self):
        try:
            self.playerActions = PlayerActions(self.driver)
            self.element_actions.wait_for_page_to_load()
            remove_unexpected_popups(self)
            self.playerActions.init_search_player_info("tallo", "600")
            run_loop(self)
            return server_status_messages.FAB_LOOP_FINISHED, 200

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            return server_status_messages.FAB_LOOP_FAILED, 404
