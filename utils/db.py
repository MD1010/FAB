from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from consts import DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, PLAYERS_COLLECTION, EA_ACCOUNTS_COLLECTION, USERS_COLLECTION, NATIONS_COLLECTION, LEAGUES_COLLECTION, \
    TEAMS_COLLECTION

try:
    cluster = MongoClient(f'mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0-qs7gn.mongodb.net/{DB_NAME}?retryWrites=true&w=majority', DB_PORT)
    fab_db = cluster[DB_NAME]
    players_collection = fab_db[PLAYERS_COLLECTION]
    ea_accounts_collection = fab_db[EA_ACCOUNTS_COLLECTION]
    users_collection = fab_db[USERS_COLLECTION]
    nations_collection = fab_db[NATIONS_COLLECTION]
    leagues_collection = fab_db[LEAGUES_COLLECTION]
    teams_collection = fab_db[TEAMS_COLLECTION]
except ConnectionFailure:
    raise Exception("connection failed")

def get_collection_documents(collection_name):
    collection = collection_name.find({}, {'_id': 0})
    res = []
    for document in collection:
        res.append(document)
    return res
