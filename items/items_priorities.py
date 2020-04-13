from consts.prices.prices_consts import MAX_PRICE
from models.price_evaluator import get_sell_price


def set_items_priorities(items, user_coin_balance):
    for item in items:
        if item['maxBIN'] > user_coin_balance:
            item['priority'] = 0
        else:
            if item.get('marketPrice'):
                item['priority'] = get_sell_price(item['marketPrice']) - item['marketPrice']
            # always prefer the unnamed search - to catch more players - give to an item that doesn't have name the biggest priority(profit)
            else:
                item['priority'] = MAX_PRICE


def get_item_to_search_according_to_prices(items):
    sorted_by_profit = sorted(items, key=lambda item: item['priority'], reverse=True)
    if _check_if_no_items_to_search_left(items):
        return None
    return sorted_by_profit[0]


def _check_if_no_items_to_search_left(items):
    for item in items:
        if item['profit'] != 0:
            return False
    return True
