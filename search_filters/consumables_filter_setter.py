import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from consts.webapp_filters.consumable_type import consumable_webapp_type_names
from enums.actions_for_execution import ElementCallback
from enums.item_types import ItemTypes
from models.search_filter_setter import SearchFilterSetter


class ConsumableFilterSetter(SearchFilterSetter):
    def __init__(self, element_actions):
        self.element_actions = element_actions

    def set_consumable_type_filter(self, consumable_type):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.CONSUMABLE_TYPE_FILTER_BTN,
                                                                              elements.CONSUMABLE_TYPE_FILTER_DROPDOWN,
                                                                              consumable_webapp_type_names.get(ItemTypes(consumable_type)))

    def set_item_quality_filter(self, consumable_quality):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.CONSUMABLES_QUALITY_FILTER_BTN,
                                                                              elements.CONSUMABLES_QUALITY_FILTER_DROPDOWN,
                                                                              consumable_quality)

    def set_specific_item_name_filter(self, consumable_name):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.CONSUMABLE_SPECIFIC_NAME_FILTER_BTN,
                                                                              elements.CONSUMABLE_SPECIFIC_NAME_FILTER_DROPDOWN,
                                                                              consumable_name)

    def set_item_price_filter(self, consumable_price):
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(consumable_price))
