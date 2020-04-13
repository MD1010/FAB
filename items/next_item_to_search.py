from consts import elements
from items.items_priorities import get_item_to_search_according_to_prices
from search_filters.filter_setter import FilterSetter
from user_info.user_actions import update_coin_balance



def update_search_item_if_coin_balance_changed(fab, best_item_to_search, items):
    new_coin_balance = int(fab.element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    if new_coin_balance != fab.user.coin_balance:
        update_coin_balance(fab.user.email, fab.element_actions)
        best_item_to_search = get_item_to_search_according_to_prices(items)
        if best_item_to_search is not None:
            FilterSetter(fab.element_actions, best_item_to_search).set_custom_search_filteres()
    return best_item_to_search
