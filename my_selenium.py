import time
from enum import Enum

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait

import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import os.path

import selenium_scripts
from helper_functions import loadCookiesFile, saveToCookiesFile

import elements
from players_actions import PlayerActions
from elements_manager import ElementCallback, ElementActions, ElementPathBy

statusCode = ''


def start_login(email, password):
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(constants.WEB_APP_URL)
        element_actions = ElementActions(driver)

        if os.path.isfile(constants.COOKIES_FILE_NAME):
            driver.delete_all_cookies()
            cookies = loadCookiesFile(constants.COOKIES_FILE_NAME)
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                driver.add_cookie(cookie)
            driver.get(constants.WEB_APP_URL)

            element_actions.execute_element_action(elements.FIRST_LOGIN, ElementCallback.CLICK, None, timeout=60)

            # Entering password left, and you are in!

            element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
            element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)

            # check if got to login page and then return response...

        # cookies file was not found - log in the first time

        else:
            driver.get(constants.SIGN_IN_URL)
            element_actions.execute_element_action(elements.EMAIL_FIELD, ElementCallback.SEND_KEYS, email)
            element_actions.execute_element_action(elements.PASSWORD_FIELD, ElementCallback.SEND_KEYS, password)
            element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)
            # check the SMS option
            element_actions.execute_element_action(elements.CODE_BTN, ElementCallback.CLICK)
            # send the sms verfication
            element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)

            while statusCode is '':
                time.sleep(1)
                pass

            # What happens if the user is stupid enough to type the wrong code ? ? ?

            # status code is set

            element_actions.execute_element_action(elements.ONE_TIME_CODE_FIELD, ElementCallback.SEND_KEYS, statusCode)
            element_actions.execute_element_action(elements.BTN_NEXT, ElementCallback.CLICK)

            eaCookies = driver.get_cookies()
            driver.get(constants.SIGN_IN_URL)
            signInCookies = driver.get_cookies()

            for cookie in signInCookies:
                if 'expiry' in cookie:
                    del cookie['expiry']
                if cookie not in eaCookies:
                    eaCookies.append(cookie)
            # takes 10-15 secs
            saveToCookiesFile(eaCookies, constants.COOKIES_FILE_NAME)
            driver.back()

        # time.sleep(15)
        tries_left = 10

        ##### Web app is working here #####

        # if popup is shown when entering the app it has to be removed
        popup = element_actions.get_clickable_element(elements.VIEW_MODAL_CONTAINER)
        if popup:
            driver.execute_script(selenium_scripts.REMOVE_CONTAINER_SCRIPT, popup)

        playerActions = PlayerActions(driver)
        playerActions.init_search_player_info("tallo", "200")

        while tries_left is not 0:
            element_actions.execute_element_action(elements.SEARCH_PLAYER_BTN, ElementCallback.CLICK)
            # players_manager.search_player(driver, tries_left % 2 == 1)
            time.sleep(1)
            tries_left -= 1

            player_bought = playerActions.buy_player()

            if player_bought:
                playerActions.list_player("500")

            if tries_left % 2 == 1:
                element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
            else:
                element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)

    except (WebDriverException, TimeoutException) as e:
        print(f"Oops :( Something went wrong.. {e.msg}")


def setStatusCode(code):
    global statusCode
    statusCode = code
