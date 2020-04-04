import json

import bcrypt

from active.data import users_attempted_login, active_fabs
from auth.login_attempt import LoginAttempt
from fab import Fab


def saveToCookiesFile(obj, name):
    with open(name, 'w') as f:
        f.write(json.dumps(obj))


def loadCookiesFile(name):
    with open(name, 'r') as f:
        return json.load(f)


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def get_user_login_attempt(email):
    return users_attempted_login[email]

def create_new_fab(driver,element_actions,email):
    fab = Fab(driver=driver, element_actions=element_actions)
    active_fabs[email] = fab
