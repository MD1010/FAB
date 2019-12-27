import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def start_login(email, password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(constants.ROOT_URL)
    # assert "EA" in driver.title

    """Getting into the login page"""
    driver.find_element_by_class_name("eas-nav_control").click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector(".eas-cta--login").click()
    driver.implicitly_wait(10)

    """In the login page-entering fields"""
    emailField = driver.find_element_by_id("email")
    passwordField = driver.find_element_by_id("password")
    logInButton = driver.find_element_by_id("btnLogin")
    emailField.send_keys(email)
    passwordField.send_keys(password)
    logInButton.click()

    """Confirmation page"""
    driver.find_element_by_class_name("btn-next").click()
    """get the confirmation password"""
    driver.implicitly_wait(20)


    confirmationCode = checkMainForConfirmation(driver,email)

    #     checkMainForConfirmation(email)
    # driver.close()


def checkMainForConfirmation(driver,email):
    #new tab
    driver.execute_script('''window.open("https://www.google.com/intl/iw/gmail/about/#","_blank");''')
    confirmationCode = ""
    return confirmationCode
