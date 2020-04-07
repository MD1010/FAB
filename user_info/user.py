from active.data import active_fabs
from consts import elements
from consts.platform import platforms
from elements.actions_for_execution import ElementCallback
from utils import db


def update_coin_balance(email, element_actions):
    current_coin_balance = int(element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))
    active_fabs[email].user.coin_balance = current_coin_balance
    db.users_collection.update({"email": email}, {"$set": {"coin_balance": current_coin_balance}})


def update_db_user_platform(email, element_actions):
    element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    db.users_collection.update({"email": email}, {"$set": {"platform": platforms[platform_icon_class]}})


def update_db_username(email, element_actions):
    element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    username = element_actions.get_element(elements.USER_NAME).text
    db.users_collection.update({"email": email}, {"$set": {"username": username}})


class User:
    def __init__(self, email, password="", cookies=None, username="", platform=""):
        if cookies is None:
            cookies = []
        self.email = email
        self.password = password
        self.cookies = cookies
        self.username = username
        self.platform = platform
        self.total_runtime = 0
        self.coin_balance = 0
        self.total_coins_earned = 0

        # active_users = [{fab,user},{fab,user}]
