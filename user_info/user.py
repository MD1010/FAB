from consts import elements
from consts.platform import platforms
from elements.actions_for_execution import ElementCallback




def get_coin_balance(self):
    coins = self.element_actions.get_element(elements.COIN_BALANCE).text
    return int(coins.replace(',', ''))

def get_user_platform(self):
    self.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = self.element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    return platforms.get(platform_icon_class)

def get_user_name(self):
    self.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    user_name = self.element_actions.get_element(elements.USER_NAME).text
    return user_name

class User:
    def __init__(self, email, password, user_name="", platform="", cookies=None):
        if cookies is None:
            cookies = []
        self.email = email
        self.password = password
        self.user_name = user_name
        self.platform = platform
        self.cookies = cookies
        self.total_runtime = 0
        self.total_coins_earned = 0



        #active_users = [{fab,user},{fab,user}]

