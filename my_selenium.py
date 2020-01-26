import json
import time

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


def setStatusCode(code):
    global statusCode
    statusCode = code
