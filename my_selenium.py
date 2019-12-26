import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def start_login(email,password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(constants.ROOT_URL)
    # assert "EA" in driver.title

    """Getting into the login page"""
    driver.find_element_by_class_name("eas-nav_control").click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector(".eas-cta--login").click()
    driver.implicitly_wait(10)

    """In the login page-entering fields"""
    email_field = driver.find_element_by_id("email")
    password_field = driver.find_element_by_id("password")
    log_in_button = driver.find_element_by_id("btnLogin")
    email_field.send_keys(email)
    password_field.send_keys(password)
    log_in_button.click()

    """Confirmation page"""
    # driver.close()
