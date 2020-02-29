import time
from enum import Enum

from selenium.common.exceptions import NoSuchElementException
import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import os.path

from helper_functions import loadCookiesFile, saveToCookiesFile
from elements_manager import ElementPathBy

import elements
import players_manager
import elements_manager

statusCode = ''

def start_login(email, password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(constants.WEB_APP_URL)

    if os.path.isfile(constants.COOKIES_FILE_NAME):
        driver.delete_all_cookies()
        cookies = loadCookiesFile(constants.COOKIES_FILE_NAME)
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)
        driver.get(constants.WEB_APP_URL)
        driver.implicitly_wait(5)

        loginButton = elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.FIRST_LOGIN, driver)
        time.sleep(1)
        loginButton.click()

        # Entering password left, and you are in!

        passwordField = elements_manager.get_clickable_element(ElementPathBy.ID, elements.PASSWORD_FIELD, driver)
        passwordField.send_keys(password)

        elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.BTN_NEXT, driver).click()

        # check if got to login page and then return response...

    # cookies file was not found - log in the first time
    else:
        driver.get(constants.SIGN_IN_URL)
        emailField = elements_manager.get_clickable_element(ElementPathBy.ID, elements.EMAIL_FIELD, driver)
        passwordField = elements_manager.get_clickable_element(ElementPathBy.ID, elements.PASSWORD_FIELD, driver)
        logInButton = elements_manager.get_clickable_element(ElementPathBy.ID, elements.LOGIN_BTN, driver)
        emailField.send_keys(email)
        passwordField.send_keys(password)
        logInButton.click()
        elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.CODE_BTN, driver).click()

        # send the sms verfication

        elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.BTN_NEXT, driver).click()

        while statusCode is '':
            time.sleep(1)
            pass

        # What happens if the user is stupid enough to type the wrong code ? ? ?

        # status code is set

        elements_manager.get_clickable_element(ElementPathBy.ID, elements.ONE_TIME_CODE_FIELD, driver).send_keys(statusCode)
        elements_manager.get_clickable_element(ElementPathBy.ID, elements.SUBMIT_BTN, driver).click()

        eaCookies = driver.get_cookies()
        driver.get(constants.SIGN_IN_URL)
        signInCookies = driver.get_cookies()

        for cookie in signInCookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            if cookie not in eaCookies:
                eaCookies.append(cookie)
        saveToCookiesFile(eaCookies, constants.COOKIES_FILE_NAME)
        driver.back()

    time.sleep(15)
    tries_left = 10

    ##### Web app is working here #####

    # if popup is shown when entering the app it has to be removed
    try:
        popup = elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.VIEW_MODAL_CONTAINER, driver)
        driver.execute_script(elements.REMOVE_CONTAINER_SCRIPT, popup)
    except NoSuchElementException:
        pass
    
    players_manager.init_search_player_info("fisker", "200", driver)

    time.sleep(1)

    while tries_left is not 0:
        elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.SEARCH_PLAYER_BTN, driver).click()
        #players_manager.search_player(driver, tries_left % 2 == 1)      
        time.sleep(1)
        tries_left -= 1

        player_bought = players_manager.buy_player(driver)
        time.sleep(2)

        if (player_bought):
            players_manager.list_player("500", driver)
        
        if tries_left % 2 == 1:
            elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.INCREASE_PRICE_BTN, driver).click()
        else:
            elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.DECREASE_PRICE_BTN, driver).click()


def setStatusCode(code):
    global statusCode
    statusCode = code