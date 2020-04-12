from models.item import Item
from models.item_with_filters import ItemWithFilters


def calculate_items_profit(user_coin_balance, requested_items_with_filters):
    for item_with_filters in requested_items_with_filters:
        item_with_filters.item.calculate_profit(user_coin_balance)


def build_item_with_filters_objects_from_dict(requested_items_with_filters):
    item_with_filters_result = []
    for item_with_filters in requested_items_with_filters:
        item_dict = item_with_filters["item"]
        filters_dict = item_with_filters["filters"]
        item_obj = Item(item_dict.get('id'), item_dict.get('name'), item_dict.get('type'))
        item_with_filters_result.append(ItemWithFilters(item_obj, filters_dict))
    requested_items_with_filters = item_with_filters_result
    return requested_items_with_filters
