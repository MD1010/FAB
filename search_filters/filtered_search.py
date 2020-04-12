from enums.filters import PlayerFilters
from factories.filters_setter import FiltersSetterFactory
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
        # if item_price_limit is None:
        #     item_price_limit = item.max_buy_price
        filter_setter = FiltersSetterFactory(self.item_with_filters.item, self.element_actions).get_filters_setter_object()

        # get existing filters from user
        for filter_name, filter_value in self.item_with_filters.filters:

            if PlayerFilters(filter_name) == PlayerFilters.NAME:
                filter_setter.set_player_name_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.QUALITY:
                filter_setter.set_player_quality_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.POSITON:
                filter_setter.set_player_position_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.CHEM:
                filter_setter.set_player_chem_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.NATION:
                filter_setter.set_player_nation_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.LEAGUE:
                filter_setter.set_player_league_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.CLUB:
                filter_setter.set_player_club_filter(filter_value)

            if PlayerFilters(filter_name) == PlayerFilters.MAX_BIN:
                filter_setter.set_player_price_filter(filter_value)

    # search_filter_setter.set_name_filter(item.name)
    # search_filter_setter.set_price_filter(item_price_limit)
