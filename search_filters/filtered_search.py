from enums.filters import PlayerFilters, ConsumableFilters
from enums.item_types import ItemTypes
from search_filters.set_consumables_search_filters import ConsumablesSearchFilterSetter
from search_filters.set_player_search_filteres import PlayerSearchFilterSetter


class FilteredSearch:
    def __init__(self, element_actions, item_with_filters):
        self.element_actions = element_actions
        self.item_with_filters = item_with_filters

    def set_basic_filters_to_get_player_price(self):
        search_filter_setter = PlayerSearchFilterSetter(self.element_actions)
        search_filter_setter.set_specific_item_name_filter(self.item_with_filters.item.get('name'))
        search_filter_setter.set_item_price_filter(self.item_with_filters.filters.get('max_bin'))

    def set_custom_search_filteres(self):
        if ItemTypes(self.item_with_filters.item.type) == ItemTypes.PLAYER:
            self._set_player_filters()
        else:
            self._set_consumable_filters()

    def _set_player_filters(self):
        player_filter_setter = PlayerSearchFilterSetter(self.element_actions)
        # set existing player filters from user
        for filter_name, filter_value in self.item_with_filters.filters:

            if PlayerFilters(filter_name) == PlayerFilters.NAME:
                player_filter_setter.set_specific_item_name_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.QUALITY:
                player_filter_setter.set_item_quality_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.POSITON:
                player_filter_setter.set_player_position_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.CHEM:
                player_filter_setter.set_player_chem_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.NATION:
                player_filter_setter.set_player_nation_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.LEAGUE:
                player_filter_setter.set_player_league_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.CLUB:
                player_filter_setter.set_player_club_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.MAX_BIN:
                player_filter_setter.set_item_price_filter(filter_value)

    def _set_consumable_filters(self):
        consumable_filter_setter = ConsumablesSearchFilterSetter(self.element_actions)
        # set existing consumable filters from user
        for filter_name, filter_value in self.item_with_filters.filters:

            if ConsumableFilters(filter_name) == ConsumableFilters.CONSUMABLE_NAME:
                consumable_filter_setter.set_specific_item_name_filter(filter_value)

            if ConsumableFilters(filter_name) == ConsumableFilters.QUALITY:
                consumable_filter_setter.set_item_quality_filter(filter_value)

            if ConsumableFilters(filter_name) == ConsumableFilters.MAX_BIN:
                consumable_filter_setter.set_item_price_filter(filter_value)
