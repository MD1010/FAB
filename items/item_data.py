from models.Item import Item


def calculate_items_profit(user_coin_balance, requested_items):
    for item_obj in requested_items:
        item_obj.calculate_profit(user_coin_balance)
    return requested_items


def build_item_objects_from_dict(requested_items):
    requested_items_obj = []
    for item in requested_items:
        item_obj = Item(item["id"], item["name"])
        requested_items_obj.append(item_obj)
    requested_items = requested_items_obj
    return requested_items
