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

    time.sleep(15)
    driver.find_element_by_xpath("/html/body/main/section/nav/button[3]").click()
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div/div[2]/div[2]").click()
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/input").send_keys("messi")
    time.sleep(1)
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div/ul/button[1]").click()
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[6]/div[2]/input").send_keys("150000")
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/input").send_keys("250")
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/button[1]").click() #decrease
    # driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/button[2]").click() #increase
    driver.find_element_by_xpath("/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[2]").click() #search
    time.sleep(2)
    no_results = driver.find_elements_by_xpath("/html/body/main/section/section/div[2]/div/div/section/div/div[2]/div/h2")
    if len(no_results) == 1:
        print("no results")
        #navigate back
        driver.find_element_by_xpath("/html/body/main/section/section/div[1]/button[1]").click()

    #if player was found
    # else:
    #     driver.find_element_by_xpath("")










def setStatusCode(code):
    global statusCode
    statusCode = code
