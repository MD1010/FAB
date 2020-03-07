from consts import elements
from elements.elements_manager import ElementCallback


def decrease_increase_min_price(self, increase_price):
    # check if price can be decreased
    el = self.element_actions.get_clickable_element(elements.DECREASE_PRICE_BTN)
    can_be_decreased = el.is_enabled()
    max_bin_price = self.element_actions.get_clickable_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value")
    can_be_increased = True if max_bin != "200" else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        self.element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        self.element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)