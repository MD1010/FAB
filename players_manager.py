import time
from enum import Enum

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import elements
import elements_manager
from elements_manager import ElementPathBy

def init_search_player_info(player_name, player_price, driver):
    # click on TRANSFERS
    elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.ICON_TRANSFER_BTN, driver).click()
    time.sleep(1)

    # click on search on transfer market
    elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.TRANSFER_MARKET_CONTAINER_BTN, driver).click()
    time.sleep(1)

    # write the searched player name
    elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.SEARCHED_PLAYER_FIELD, driver).send_keys(player_name)
    time.sleep(1)

    # choose the player in the list(the first one)
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.FIRST_RESULT_INPUT_SEARCH, driver).click()
    time.sleep(1)

    # set max BIN price - clear the input first
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT, driver).clear()
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT, driver).send_keys(player_price)

    # time.sleep(1)

    # set min price - clear the input first
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT, driver).clear()
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT, driver).send_keys(player_price)

    time.sleep(1)

def search_player(driver, bin_increase = True):
    # search
    elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.SEARCH_PLAYER_BTN, driver).click()

    if bin_increase:
        elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.INCREASE_PRICE_BTN, driver).click()
    else:
        elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.DECREASE_PRICE_BTN, driver).click()

def buy_player(driver):
    try:
        elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.BUY_BTN, driver).click()
        # 1 - buy , 2-cancel - cancel when testing
        # buy the player
        elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.CONFIRM_BUY_BTN, driver).click()
        return True
    # ????? navigating back too slowly ????? - happends because find element by xpath takes time...
    except NoSuchElementException:
        # if no players to the wanted price were found - navigate back
        elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.NAVIGATE_BACK, driver).click()
        return False

def list_player(price, driver):
    # Button to start the listing quickly after buying (not through user transfer list) 
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.LIST_ON_TRANSFER_BTN, driver).click()
    time.sleep(2)

    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, driver).send_keys(Keys.CONTROL, "a")
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MAX_BIN_PRICE_INPUT_AFTER_LIST, driver).send_keys(price)
    time.sleep(2)

    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, driver).send_keys(Keys.CONTROL, "a")
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.MIN_BIN_PRICE_INPUT_AFTER_LIST, driver).send_keys(price)
    time.sleep(2)

    # List player on transfer market
    elements_manager.get_clickable_element(ElementPathBy.XPATH, elements.LIST_ITEM_ON_TRANSFER_LIST, driver).click()
    time.sleep(2)

    # Navigate back after player was listed
    elements_manager.get_clickable_element(ElementPathBy.CLASS_NAME, elements.NAVIGATE_BACK, driver).click()