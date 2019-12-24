import constants

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def start_login():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(constants.ROOT_URL)
    print (driver.title)
    assert "EA" in driver.title
    driver.close()
