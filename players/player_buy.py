import time
from consts import elements
from consts.app import ONE_SEARCH_DELTA
from elements.elements_manager import ElementCallback
from players.models.player import Player


def decrease_increase_min_price(self, increase_price):
    # check if price can be decreased
    decrease_btn = self.element_actions.get_element(elements.DECREASE_PRICE_BTN)
    can_be_decreased = decrease_btn.is_enabled() if decrease_btn else False
    max_bin_price = self.element_actions.get_element(elements.MAX_BIN_PRICE_INPUT)
    max_bin = max_bin_price.get_attribute("value") if max_bin_price else "200"
    can_be_increased = True if max_bin != "200" else False
    # dont increase when max bin is 200
    # increase min price according to the loop counter
    if can_be_increased and increase_price:
        self.element_actions.execute_element_action(elements.INCREASE_PRICE_BTN, ElementCallback.CLICK)
    if not increase_price and can_be_decreased:
        self.element_actions.execute_element_action(elements.DECREASE_PRICE_BTN, ElementCallback.CLICK)

## dont-forget -- player is used now- don't repeat him so remove from the requested_players
def _decide_player_buy_price(requested_players):
    # get that from web app
    # get that data as a param from the route - that will receive this in req.body
    # requested_players = [
    #
    #     Player("20801", "Cristiano Ronaldo", 93, 520000),
    #
    #     Player("173731", "Gareth Bale", 85, 9000),
    #
    #     Player("158023", "Lionel Messi", 94, 490000),
    #
    # ]
    sorted_by_profit = sorted(requested_players, key=lambda player: player.profit,reverse=True)

    most_profitable_player = sorted_by_profit[0]

    # if all the players are above the budget
    if most_profitable_player.profit == 0:
        return None
    else:
        return sorted_by_profit[0].name

def allocate_loop_number_for_players(requested_players,total_time):
    total_profit = sum(player.profit for player in requested_players)
    loop_times = [round(player.profit/total_profit * total_time) for player in requested_players]
    #add 0.5 to round up - to prevent the autobuyer from doing nothing when time left
    number_of_loops = [round((loop_time/ONE_SEARCH_DELTA)+0.5) for loop_time in loop_times]
    players_names = list(map(lambda player: player.name,requested_players))
    allocated_jobs = dict(zip(players_names, number_of_loops))
    return allocated_jobs
