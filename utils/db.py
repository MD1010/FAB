from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from consts import DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, PLAYERS_COLLECTION, EA_ACCOUNTS_COLLECTION, USERS_COLLECTION

try:
    cluster = MongoClient(f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0-qs7gn.mongodb.net/{DB_NAME}?retryWrites=true&w=majority', DB_PORT)
    fab_db = cluster[DB_NAME]
    players_collection = fab_db[PLAYERS_COLLECTION]
    ea_accounts_collection = fab_db[EA_ACCOUNTS_COLLECTION]
    users_collection = fab_db[USERS_COLLECTION]
except ConnectionFailure:
    raise Exception("connection failed")
