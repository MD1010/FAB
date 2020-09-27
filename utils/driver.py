from typing import Dict

from selenium.webdriver.chrome.webdriver import WebDriver
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from consts import app
from src.web_app.live_logins import login_attempts

opened_drivers: Dict[str, 'WebDriver'] = {}
def get_or_create_driver_instance(email):
    if opened_drivers.get(email):
        return opened_drivers[email]
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(app.WEB_APP_URL)
        opened_drivers[email] = driver
        return driver

def close_driver(email):
    driver = opened_drivers.get(email)
    if driver:
        driver.quit()
        if login_attempts.get(email):
            del login_attempts[email]


