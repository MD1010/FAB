from consts import elements
from enums.actions_for_execution import ElementCallback
from enums.filters import PlayerFilters, ConsumableFilters
from enums.item_types import ItemTypes
from search_filters.consumables_filter_setter import ConsumableFilterSetter
from search_filters.players_filter_setter import PlayerFilterSetter


class FilterSetter:
    def __init__(self, element_actions, item):
        self.element_actions = element_actions
        self.item = item

    def set_basic_filters_to_get_item_price(self, futbin_price):
        if ItemTypes(self.item.type) == ItemTypes.PLAYER:
            # go to the players tab
            self.element_actions.execute_element_action(elements.PLAYERS_TAB_BUTTON, ElementCallback.CLICK)
            search_filter_setter = PlayerFilterSetter(self.element_actions)
            search_filter_setter.set_specific_item_name_filter(self.item.name)
            search_filter_setter.set_item_price_filter(futbin_price)
        else:
            # go to the consumables tab
            self.element_actions.execute_element_action(elements.CONSUMABLES_TAB_BUTTON, ElementCallback.CLICK)
            self._set_consumable_filters()

    def set_custom_search_filteres(self):
        if ItemTypes(self.item.type) == ItemTypes.PLAYER:
            # go to the players tab
            self.element_actions.execute_element_action(elements.PLAYERS_TAB_BUTTON, ElementCallback.CLICK)
            self._set_player_filters()
        else:
            # go to the consumables tab
            self.element_actions.execute_element_action(elements.CONSUMABLES_TAB_BUTTON, ElementCallback.CLICK)
            self._set_consumable_filters()

    def _set_player_filters(self):
        player_filter_setter = PlayerFilterSetter(self.element_actions)
        # set existing player webapp_filters from user
        for filter_name, filter_value in self.item.filters.items():

            if PlayerFilters(filter_name) == PlayerFilters.NAME:
                player_filter_setter.set_specific_item_name_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.QUALITY:
                player_filter_setter.set_item_quality_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.POSITON:
                player_filter_setter.set_player_position_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.CHEM:
                player_filter_setter.set_player_chem_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.NATION and not self.item.get('name'):
                player_filter_setter.set_player_nation_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.LEAGUE and not self.item.get('name'):
                player_filter_setter.set_player_league_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.CLUB and not self.item.get('name'):
                player_filter_setter.set_player_club_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.MAX_BIN:
                player_filter_setter.set_item_price_filter(filter_value)

    def _set_consumable_filters(self):
        consumable_filter_setter = ConsumableFilterSetter(self.element_actions)
        # set existing consumable webapp_filters from user
        for filter_name, filter_value in self.item:

            if ConsumableFilters(filter_name) == ConsumableFilters.CONSUMABLE_NAME:
                consumable_filter_setter.set_specific_item_name_filter(filter_value)

            if ConsumableFilters(filter_name) == ConsumableFilters.QUALITY:
                consumable_filter_setter.set_item_quality_filter(filter_value)

            if ConsumableFilters(filter_name) == ConsumableFilters.MAX_BIN:
                consumable_filter_setter.set_item_price_filter(filter_value)
