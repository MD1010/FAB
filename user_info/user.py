from consts import elements
from consts.platform import platforms
from elements.actions_for_execution import ElementCallback

user_platform = ''
user_name = ''
coin_balance = 0

def get_coin_balance(self):
    coins = self.element_actions.get_element(elements.COIN_BALANCE).text
    return int(coins.replace(',', ''))

def get_user_platform(self):
    self.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = self.element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    return platforms.get(platform_icon_class)

