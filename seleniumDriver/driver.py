from webdriver_manager.chrome import ChromeDriverManager

from consts import app
from selenium import webdriver

class Driver:
    def __init__(self,driver):
        self.driver = driver

def initialize_driver(self):
    self.driver = webdriver.Chrome(ChromeDriverManager().install())
    self.driver.get(app.WEB_APP_URL)
    # self.driver.find_element_by_xpath().

