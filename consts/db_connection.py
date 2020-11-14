import os

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT'))

PLAYERS_COLLECTION = "players"
EA_ACCOUNTS_COLLECTION = "accounts"
USERS_COLLECTION = "users"
NATIONS_COLLECTION = "nations"
LEAGUES_COLLECTION = "leagues"
TEAMS_COLLECTION = "teams"
