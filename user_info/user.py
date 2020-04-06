from consts import elements
from consts.platform import platforms
from elements.actions_for_execution import ElementCallback
from utils import db
from utils.helper_functions import get_user_from_db_if_exists, get_user_by_email_from_db


def update_coin_balance(fab):
    fab.user_coin_balance = int(fab.element_actions.get_element(elements.COIN_BALANCE).text.replace(',', ''))





def update_user_platform(fab):
    fab.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    platform_icon_class = fab.element_actions.get_element(elements.PLATFORM_ICON).get_attribute("class")
    db.users_collection.update({"email": fab.running_user_email}, {"$set": {"platform": platform_icon_class}})


def update_user_name(fab):
    fab.element_actions.execute_element_action(elements.SETTINGS_ICON, ElementCallback.CLICK)
    user_name = fab.element_actions.get_element(elements.USER_NAME).text
    db.users_collection.update({"email": fab.running_user_email}, {"$set": {"user_name": user_name}})


class User:
    def __init__(self, email, password="", cookies=None):
        if cookies is None:
            cookies = []
        self.email = email
        self.password = password
        self.user_name = ""
        self.platform = ""
        self.cookies = cookies
        self.coin_balance = 0
        self.total_runtime = 0
        self.total_coins_earned = 0

        # active_users = [{fab,user},{fab,user}]
