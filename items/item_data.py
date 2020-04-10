from models.Item import Item


def fill_items_value_data(user_coin_balance, requested_items, real_prices):
    result = []
    requested_items = build_item_objects_from_dict(requested_items)
    for item_obj in requested_items:
        player_market_price = 0
        for price_obj in real_prices:
            for name in price_obj.keys():
                if name == item_obj.name:
                    player_market_price = price_obj[name]
                    break
        item_obj.set_market_price(player_market_price)
        item_obj.calculate_profit(user_coin_balance)
        result.append(item_obj)
    return result


def build_item_objects_from_dict(requested_items):
    for item in requested_items:
        player_obj = Item()
        for key, value in item.items():
            setattr(player_obj, key, value)
    return requested_items
