import os

APP_SECRET_KEY = 'EA708E8DE7AACDFCAB0A7351714682CCCD906591C27E0DF23E1D77880995566A'
ROOT_URL = 'https://www.easports.com'
BASE_URL = 'fifa/ultimate-team/web-application/content'
WEB_APP_URL = "https://www.easports.com/fifa/ultimate-team/web-app/"
CONFIG_URL = 'https://www.easports.com/fifa/ultimate-team/web-app/config/config.json'
CONFIG_JSON_SUFFIX = "fut/config/companion/remoteConfig.json"
PIN_DICT = {"b": True, "bf": 500, "bs": 10, "e": True, "r": 3, "rf": 300}
CONTENT_URL = "https://www.easports.com/fifa/ultimate-team/web-app/content/"
GUID = '20C1B296-B15C-4F72-AF0F-882F187EC2C9'
YEAR = 2020
PRE_GAME_SKU = 'FFA20'
SHARDS_V2 = "ut/shards/v2"
ACOUNTS_INFO = "user/accountinfo"
PRE_SKU = 'FUT20'
SKU_B = 'FFT20'
CLIENT_VERSION = 1
GAME_URL = 'ut/game/fifa20'
PLAYERS_JSON = 'players.json'
EA_WEB_APP_URL = 'https://www.easports.com/fifa/ultimate-team/web-app/'
PIDS_ME_URL = 'https://gateway.ea.com/proxy/identity/pids/me'
REDIRECT_URI_WEB_APP = 'https://www.easports.com/fifa/ultimate-team/web-app/auth.html'
WEB_APP_AUTH = 'https://accounts.ea.com/connect/auth'
FUTBIN_PLAYER_PRICE_URL = 'https://www.futbin.com/20/playerPrices?player='
FUTHEAD_PLAYER = 'https://www.futhead.com/quicksearch/player/20/?term='
REQUEST_TIMEOUT = 15
PROFIT_MULTIPLIER = 0.075
EA_TAX = 0.95
APP_VERSION = "20.5.0"
# IN SECS
AMOUNT_OF_SEARCHES_BEFORE_SLEEP = 20
SLEEP_MID_OPERATION_DURATION = 10
ONE_SEARCH_DELTA = 10
NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH = 5
MAX_CARD_ON_PAGE = 21
FUT_HOST = {
    'pc': 'utas.external.s2.fut.ea.com:443',
    'ps3': 'utas.external.s2.fut.ea.com:443',
    'ps4': 'utas.external.s2.fut.ea.com:443',
    'xbox': 'utas.external.s3.fut.ea.com:443',
    'xbox360': 'utas.external.s3.fut.ea.com:443',
}
DS_JS_PATH = os.path.abspath(f'{os.path.dirname(os.path.abspath(""))}/utils/ds.js')
