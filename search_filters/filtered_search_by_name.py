from search_filters.set_search_filteres import SearchFilterSetter
from search_filters.filtered_search import FilteredSearch


class NameFilteredSearch(FilteredSearch):
    def set_search_filteres(self, element_actions, item, item_price_limit=None, custom_filters=None):
        item_name = item.name
        if item_price_limit is None:
            item_price_limit = item.max_buy_price
        SearchFilterSetter(element_actions).set_name_and_price_filters(item_name, item_price_limit)
