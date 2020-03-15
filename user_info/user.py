from consts import elements
from elements.models.actions_for_execution import ElementCallback
from user_info.platform import XBOX,PC,PS

user_platform = ''
user_name = ''
coin_balance = 0


def get_coin_balance(self):
    coins = self.element_actions.get_element(elements.COIN_BALANCE).text
    return int(coins.replace(',', ''))

def get_user_platform(self):
    self.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = self.element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    if XBOX in str(platform_icon_class).lower():
        return XBOX
    if PS in str(platform_icon_class).lower():
        return PS
    if PC in str(platform_icon_class).lower():
        return PC

