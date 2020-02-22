import time

from selenium.common.exceptions import NoSuchElementException

import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import os.path

from helper_functions import loadCookiesFile, saveToCookiesFile

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

        loginButton = driver.find_element_by_xpath("/html/body/main/div/div/div/button[1]")
        time.sleep(1)
        loginButton.click()

        # Entering password left, and you are in!

        passwordField = driver.find_element_by_id("password")
        passwordField.send_keys(password)

        driver.find_element_by_class_name("btn-next").click()

        # check if got to login page and then return response...

    # cookies file was not found - log in the first time
    else:
        driver.get(constants.SIGN_IN_URL)
        emailField = driver.find_element_by_id("email")
        passwordField = driver.find_element_by_id("password")
        logInButton = driver.find_element_by_id("btnLogin")
        emailField.send_keys(email)
        passwordField.send_keys(password)
        logInButton.click()
        driver.find_element_by_xpath("//input[@name='codeType' and @value='SMS']").click()

        # send the sms verfication

        driver.find_element_by_class_name("btn-next").click()

        while statusCode is '':
            time.sleep(1)
            pass

        # What happens if the user is stupid enough to type the wrong code ? ? ?

        # status code is set

        driver.find_element_by_id("oneTimeCode").send_keys(statusCode)
        driver.find_element_by_id("btnSubmit").click()

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
        popup = driver.find_element_by_class_name("view-modal-container")
        driver.execute_script("""var element = arguments[0];element.parentNode.removeChild(element);""", popup)
    except NoSuchElementException:
        pass
    # click on TRANSFERS
    driver.find_element_by_class_name("icon-transfer").click()
    time.sleep(2)

    # click on search on transfer market
    driver.find_element_by_class_name("ut-tile-transfer-market").click()
    time.sleep(1)

    # write the searched player name
    driver.find_element_by_class_name("ut-text-input-control").send_keys("messi")
    time.sleep(1)

    # choose the player in the list(the first one)
    driver.find_element_by_class_name("playerResultsList").find_elements_by_tag_name("button")[0].click()
    time.sleep(1)

    # set max BIN price - clear the input first
    driver.find_elements_by_class_name(
        "ut-numeric-input-spinner-control")[3].find_element_by_class_name("numericInput").clear()
    driver.find_elements_by_class_name(
        "ut-numeric-input-spinner-control")[3].find_element_by_class_name("numericInput").send_keys(
        "200")
    # time.sleep(1)

    # set min price - clear the input first
    driver.find_elements_by_class_name(
        "ut-numeric-input-spinner-control")[2].find_element_by_class_name("numericInput").clear()
    driver.find_elements_by_class_name(
        "ut-numeric-input-spinner-control")[2].find_element_by_class_name("numericInput").send_keys("250")
    # time.sleep(1)

    while tries_left is not 0:
        # search
        driver.find_element_by_class_name("call-to-action").click()
        # time.sleep(2)
        tries_left -= 1

        # if no players to the wanted price were found - navigate back
        try:
            driver.find_element_by_class_name("ut-no-results-view")
            # navigate back
            driver.find_element_by_class_name("ut-navigation-button-control").click()
            if tries_left % 2 == 1:
                driver.find_elements_by_class_name(
                    "ut-numeric-input-spinner-control")[2].find_element_by_class_name("increment-value").click()  # increase
            else:
                driver.find_elements_by_class_name(
                    "ut-numeric-input-spinner-control")[2].find_element_by_class_name("decrement-value").click()  # decrease
        #player was found
        except NoSuchElementException:
            try:
                driver.find_element_by_class_name("buyButton").click()
                #buy the player
                # driver.find_element_by_xpath("//*[text()[contains(., 'Cancel')]]").click()
                # print(driver.find_element_by_class_name("ut-button-group").find_elements_by_tag_name("button")[1])
            except NoSuchElementException:
                pass




        # if player was found
        # else:
        #     driver.find_element_by_xpath("")


def setStatusCode(code):
    global statusCode
    statusCode = code
