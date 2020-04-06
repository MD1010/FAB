import json

import bcrypt

from active.data import active_fabs
from fab import Fab


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def create_new_fab(driver, element_actions, player_actions, user):
    fab = Fab(driver=driver, element_actions=element_actions, player_actions=player_actions, user=user)
    active_fabs[user.email] = fab
    return fab

