from models.Item import Item
from models.ItemWithFilters import ItemWithFilters


def calculate_items_profit(user_coin_balance, requested_items):
    for item_obj in requested_items:
        item_obj.calculate_profit(user_coin_balance)
    return requested_items


def build_item_with_filters_objects_from_dict(requested_items_with_filters):
    item_with_filters_result = []
    for item_with_filters in requested_items_with_filters:
        item_dict = item_with_filters["item"]
        filters_dict = item_with_filters["filters"]
        # filters_obj = FiltersFactory(dict_item, dict_filters).get_filters_object()
        item_obj = Item(item_dict.get('id'), item_dict.get('name'), item_dict.get('type'))
        item_with_filters = ItemWithFilters(item_obj,filters_dict)
        item_with_filters_result.append(item_with_filters)
        requested_items_with_filters = item_with_filters_result
    return requested_items_with_filters

# # get the item part from the
# def get_item_objects(requested_items_with_filters):
#     requested_items = []
#     for item_with_filters in requested_items_with_filters:
#         requested_items.append(item_with_filters.item)
#     return requested_items
