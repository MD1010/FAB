from consts import elements
from items.item_data import calculate_items_profit
from search_filters.filter_setter import FilterSetter
from user_info.user_actions import update_coin_balance


def get_next_option_to_search(user_coin_balance, search_options):
    calculate_items_profit(user_coin_balance, search_options)
    sorted_by_profit = sorted(search_options, key=lambda search_option: search_option.item.profit, reverse=True)
    most_profitable_item = sorted_by_profit[0]
    # if all the players are above the budget
    if most_profitable_item.item.profit == 0:
        return None
    else:
        return sorted_by_profit[0]


def update_search_item_if_coin_balance_changed(fab, best_search_option, search_options):
    new_coin_balance = int(fab.element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    if new_coin_balance != fab.user.coin_balance:
        update_coin_balance(fab.user.email, fab.element_actions)
        best_search_option = get_next_option_to_search(fab.user.coin_balance, search_options)
        if best_search_option is not None:
            FilterSetter(fab.element_actions, best_search_option).set_custom_search_filteres()
    return best_search_option
