import time

from selenium.webdriver.common.keys import Keys

from consts import elements
from enums.actions_for_execution import ElementCallback
from models.search_filter_setter import SearchFilterSetter


class PlayerFilterSetter(SearchFilterSetter):
    def __init__(self, element_actions):
        self.element_actions = element_actions

    def set_specific_item_name_filter(self, player_name):
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.SEARCHED_PLAYER_FIELD, ElementCallback.SEND_KEYS, player_name)
        self.element_actions.execute_element_action(elements.FIRST_RESULT_INPUT_SEARCH, ElementCallback.CLICK)

    def set_item_price_filter(self, player_price):
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, Keys.CONTROL, "a")
        time.sleep(1)
        self.element_actions.execute_element_action(elements.MAX_BIN_PRICE_INPUT, ElementCallback.SEND_KEYS, str(player_price))

    def set_item_quality_filter(self, player_quality):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.PLAYER_QUALITY_FILTER_BTN,
                                                                              elements.PLAYER_QUALITY_FILTER_DROPDOWN,
                                                                              player_quality)

    def set_player_position_filter(self, player_position):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.PLAYER_POSITION_FILTER_BTN,
                                                                              elements.PLAYER_POSITION_FILTER_DROPDOWN,
                                                                              player_position)

    def set_player_chem_filter(self, player_chem):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.PLAYER_CHEM_STYLE_FILTER_BTN,
                                                                              elements.PLAYER_CHEM_FILTER_DROPDOWN,
                                                                              player_chem)

    def set_player_nation_filter(self, player_nation):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.PLAYER_NATIONALITY_FILTER_BTN,
                                                                              elements.PLAYER_NATIONALITY_FILTER_DROPDOWN,
                                                                              player_nation)

    def set_player_league_filter(self, player_league):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.PLAYER_LEAGUE_FILTER_BTN,
                                                                              elements.PLAYER_LEAGUE_FILTER_DROPDOWN,
                                                                              player_league)

    def set_player_club_filter(self, player_club):
        self.element_actions.select_matching_li_by_text_from_dropdown_ul_list(elements.CLUB_FILTER_BTN,
                                                                              elements.CLUB_FILTER_DROPDOWN,
                                                                              player_club)
