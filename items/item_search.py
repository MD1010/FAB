from abc import abstractmethod,ABC

from items.item_data import fill_items_value_data


def get_next_item_to_search(user_coin_balance, requested_items, real_prices):
    requested_items = list(fill_items_value_data(user_coin_balance, requested_items, real_prices))
    sorted_by_profit = sorted(requested_items, key=lambda item: item.profit, reverse=True)
    most_profitable_item = sorted_by_profit[0]
    # if all the players are above the budget
    if most_profitable_item.profit == 0:
        return None
    else:
        return sorted_by_profit[0]


