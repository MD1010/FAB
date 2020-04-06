import os

APP_SECRET_KEY = 'EA708E8DE7AACDFCAB0A7351714682CCCD906591C27E0DF23E1D77880995566A'
ROOT_URL = 'https://www.easports.com'
BASE_URL = 'fifa/ultimate-team/web-app/content'
WEB_APP_URL = "https://www.easports.com/fifa/ultimate-team/web-app/"
GUID = '20C1B296-B15C-4F72-AF0F-882F187EC2C9'
YEAR = '2020'
CONTENT_URL = 'fut/items/web'
PLAYERS_JSON = 'players.json'
SIGN_IN_URL = 'https://signin.ea.com/p/web2/login?execution=e1639509631s1&initref=https%3A%2F%2Faccounts.ea.com%3A443%2Fconnect%2Fauth%3Fprompt%3Dlogin%26accessToken%3Dnull%26client_id%3DFIFA-20-WEBCLIENT%26response_type%3Dtoken%26display%3Dweb2%252Flogin%26locale%3Den_US%26redirect_uri%3Dhttps%253A%252F%252Fwww.easports.com%252Ffifa%252Fultimate-team%252Fweb-app%252Fauth.html%26release_type%3Dprod%26scope%3Dbasic.identity%2Boffline%2Bsignin%2Bbasic.entitlement%2Bbasic.persona'
COOKIES_FILE_NAME = 'cookies.txt'
FUTBIN_PLAYER_PRICE_URL = 'https://www.futbin.com/20/playerPrices?player='
FUTHEAD_PLAYER = 'https://www.futhead.com/quicksearch/player/20/?term='
PROFIT_MULTIPLIER = 0.075
EA_TAX = 0.95
# IN SECS
AMOUNT_OF_SEARCHES_BEFORE_SLEEP = 20
SLEEP_MID_OPERATION_DURATION = 10
ONE_SEARCH_DELTA = 10
CHROME_DRIVER_PROCESS_NAME = "chromedriver.exe"
NUMBER_OF_SEARCHS_BEFORE_BINARY_SEARCH = 5
MAX_CARD_ON_PAGE = 20
users_rooms = {}
CURRENT_WORKING_DIR = os.path.abspath(os.getcwd())
STATUS_CODE_TRIES = 5
TIME_TO_LOGIN = 180

