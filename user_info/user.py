from consts import elements

platform = ''
user_name = ''
coin_balance = 0


def get_coin_balance(self):
    coins = self.element_actions.get_element(elements.COIN_BALANCE).text
    return int(coins.replace(',', ''))