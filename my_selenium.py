import time
from enum import Enum

from selenium.common.exceptions import NoSuchElementException

import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import os.path

from helper_functions import loadCookiesFile, saveToCookiesFile

import elements

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

        loginButton = get_clickable_element(ElementPathBy.XPATH, elements.FIRST_LOGIN, driver)
        time.sleep(1)
        loginButton.click()

        # Entering password left, and you are in!

        passwordField = get_clickable_element(ElementPathBy.ID, elements.PASSWORD_FIELD, driver)
        passwordField.send_keys(password)

        get_clickable_element(ElementPathBy.CLASS_NAME, elements.BTN_NEXT, driver).click()

        # check if got to login page and then return response...

    # cookies file was not found - log in the first time
    else:
        driver.get(constants.SIGN_IN_URL)
        emailField = get_clickable_element(ElementPathBy.ID, elements.EMAIL_FIELD, driver)
        passwordField = get_clickable_element(ElementPathBy.ID, elements.PASSWORD_FIELD, driver)
        logInButton = get_clickable_element(ElementPathBy.ID, elements.LOGIN_BTN, driver)
        emailField.send_keys(email)
        passwordField.send_keys(password)
        logInButton.click()
        get_clickable_element(ElementPathBy.XPATH, elements.CODE_BTN, driver).click()

        # send the sms verfication

        get_clickable_element(ElementPathBy.CLASS_NAME, elements.BTN_NEXT, driver).click()

        while statusCode is '':
            time.sleep(1)
            pass

        # What happens if the user is stupid enough to type the wrong code ? ? ?

        # status code is set

        get_clickable_element(ElementPathBy.ID, elements.ONE_TIME_CODE_FIELD, driver).send_keys(statusCode)
        get_clickable_element(ElementPathBy.ID, elements.SUBMIT_BTN, driver).click()

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

    # if popup is shown when entering the app it has to be removed
    try:
        popup = get_clickable_element(ElementPathBy.CLASS_NAME, elements.VIEW_MODAL_CONTAINER, driver)
        driver.execute_script(elements.REMOVE_CONTAINER_SCRIPT, popup)
    except NoSuchElementException:
        pass
    # click on TRANSFERS
    get_clickable_element(ElementPathBy.CLASS_NAME, elements.ICON_TRANSFER_BTN, driver).click()
    time.sleep(1)

    # click on search on transfer market
    get_clickable_element(ElementPathBy.CLASS_NAME, elements.TRANSFER_MARKET_CONTAINER_BTN, driver).click()
    time.sleep(1)

    # write the searched player name
    get_clickable_element(ElementPathBy.CLASS_NAME, elements.SEARCHED_PLAYER_FIELD, driver).send_keys("messi")
    time.sleep(1)

    # choose the player in the list(the first one)
    get_clickable_element(ElementPathBy.XPATH, elements.FIRST_RESULT_INPUT_SEARCH, driver).click()
    time.sleep(1)

    # set max BIN price - clear the input first
    get_clickable_element(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT, driver).clear()
    get_clickable_element(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT, driver).send_keys("200")

    # time.sleep(1)

    # set min price - clear the input first
    get_clickable_element(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT, driver).clear()
    get_clickable_element(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT, driver).send_keys("200")

    time.sleep(1)

    while tries_left is not 0:
        # search
        get_clickable_element(ElementPathBy.CLASS_NAME, elements.SEARCH_PLAYER_BTN, driver).click()

        time.sleep(1)
        tries_left -= 1

        # try to buy
        try:
            get_clickable_element(ElementPathBy.CLASS_NAME, elements.BUY_BTN, driver).click()
            # 1 - buy , 2-cancel - cancel when testing
            # buy the player
            get_clickable_element(ElementPathBy.XPATH, elements.CANCEL_BUY_BTN, driver).click()

        # ????? navigating back too slowly ????? - happends because find element by xpath takes time...
        except NoSuchElementException:
            # if no players to the wanted price were found - navigate back
            get_clickable_element(ElementPathBy.CLASS_NAME, elements.NAVIGATE_BACK, driver).click()

            if tries_left % 2 == 1:
                get_clickable_element(ElementPathBy.XPATH, elements.INCREASE_PRICE_BTN, driver).click()

            else:
                # decrease
                get_clickable_element(ElementPathBy.XPATH, elements.DECREASE_PRICE_BTN, driver).click()


def setStatusCode(code):
    global statusCode
    statusCode = code


class ElementPathBy(Enum):
    CLASS_NAME = 0
    XPATH = 1
    ID = 2


def throw_if_element_unreachable(get_element_func) -> "throws error if element is not found":
    print("in throw if element is unreachable")

    def throw(*args, **kwargs):
        try:
            return get_element_func(*args, **kwargs)
        except NoSuchElementException:
            print("in except")
            raise NoSuchElementException(f"Element {args[1]} was not found!")

    return throw


@throw_if_element_unreachable
def get_clickable_element(element_path_by: 'xpath/className/id path', path: 'actual element path',
                          driver) -> "return the wanted element if exists":
    # check_element_in_local_storage()
    switcher = {
        ElementPathBy.CLASS_NAME: driver.find_element_by_class_name,
        ElementPathBy.XPATH: driver.find_element_by_xpath,
        ElementPathBy.ID: driver.find_element_by_id
    }
    return switcher[element_path_by](path)
    # if len(element_list_result) == 0:
    #     raise NoSuchElementException()
    # return element_list_result[element_index]
