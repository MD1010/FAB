from items.item_data import calculate_items_profit


def get_next_item_to_search(user_coin_balance, requested_items):
    requested_items = list(calculate_items_profit(user_coin_balance, requested_items))
    sorted_by_profit = sorted(requested_items, key=lambda item: item.profit, reverse=True)
    most_profitable_item = sorted_by_profit[0]
    # if all the players are above the budget
    if most_profitable_item.profit == 0:
        return None
    else:
        return sorted_by_profit[0]


