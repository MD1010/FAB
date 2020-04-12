from models.item import Item
from models.search_option import SearchOption


def calculate_items_profit(user_coin_balance, search_options):
    for search_option in search_options:
        search_option.item.calculate_profit(user_coin_balance)


def build_search_option_objects_from_dict(search_options):
    search_options_result = []
    for search_option in search_options:
        item_dict = search_option["item"]
        filters_dict = search_option["filters"]
        item_obj = Item(item_dict.get('id'), item_dict.get('name'), item_dict.get('type'))
        search_options_result.append(SearchOption(item_obj, filters_dict))
    search_options = search_options_result
    return search_options
