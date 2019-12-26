import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def start_login(email,password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(constants.ROOT_URL)
    # assert "EA" in driver.title
    driver.find_element_by_class_name("eas-nav_control").click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector(".eas-cta--login").click()
    driver.implicitly_wait(10)
    email_field = driver.find_element_by_id("email")
    password_field = driver.find_element_by_id("password")
    log_in_button = driver.find_element_by_id("btnLogin")
    email_field.send_keys(email)
    password_field.send_keys(password)
    log_in_button.click()
    # driver.close()
