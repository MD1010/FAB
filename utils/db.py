from pymongo import MongoClient
from consts.db_connection import DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, PLAYERS_COLLECTION, USERS_COLLECTION

cluster = MongoClient(f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0-qs7gn.mongodb.net/{DB_NAME}?retryWrites=true&w=majority', DB_PORT)
fab_db = cluster[DB_NAME]
players_collection = fab_db[PLAYERS_COLLECTION]
users_collection = fab_db[USERS_COLLECTION]

