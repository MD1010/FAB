import time

from consts import elements
from consts.prices import MIN_PRICE
from elements.actions_for_execution import ElementCallback


def enter_transfer_market(self):
    # click on TRANSFERS
    self.element_actions.execute_element_action(elements.ICON_TRANSFER_BTN, ElementCallback.CLICK)
    # click on search on transfer market
    self.element_actions.execute_element_action(elements.TRANSFER_MARKET_CONTAINER_BTN, ElementCallback.CLICK)
    time.sleep(1)

def decrease_increase_min_price(self, increase_price):
    # check if price can be decreased
    decrease_btn = self.element_actions.get_element(elements.DECREASE_MIN_PRICE_BTN)
    can_be_decreased = decrease_btn.is_enabled() if decrease_btn else False
    max_bin_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value") if max_bin_price else str(MIN_PRICE)
    can_be_increased = True if max_bin != str(MIN_PRICE) else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        self.element_actions.execute_element_action(elements.INCREASE_MIN_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        self.element_actions.execute_element_action(elements.DECREASE_MIN_PRICE_BTN, ElementCallback.CLICK)
