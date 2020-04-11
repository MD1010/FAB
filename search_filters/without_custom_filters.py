from players.player_init_market_search import SearchFilterSetter
from search_filters.filtered_search import FilteredSearch


class SearchWithoutCustomFilters(FilteredSearch):
    def set_search_filteres(self, element_actions, item, custom_filters=None):
        item_name = item.name
        item_price_limit = item.get_max_buy_price()
        SearchFilterSetter(element_actions).set_name_and_price_filters(item_name, item_price_limit)
