import time
from random import random

import requests

from consts import GAME_URL, REQUEST_TIMEOUT
from src.auth.live_logins import authenticated_accounts


from utils.exceptions import TimeoutError, UnknownError, ExpiredSession, Conflict, TooManyRequests, Captcha, PermissionDenied, MarketLocked, TemporaryBanned, \
    NoTradeExistingError

# this class will be vreated ouside the fab loop -> the decorator of the /start-fab will insure that the account is authenticated
class WebappActions:
    def __init__(self, ea_account):
        self.login_instance = authenticated_accounts.get(ea_account)
        self.host = self.login_instance.fut_host
        self.request_session = self.login_instance.request_session
        self.request_count = 0
        self.credits = 0
        self.duplicates = 0

    def webapp_request(self, method, url, data=None, params=None):
        self.request_count += 1
        data = data or {}
        params = params or {}
        url = f'https://{self.host}/{GAME_URL}/{url}'
        # respect min wait time between requests
        time.sleep(random.unform(1.1, 2.5))
        self.request_session.options(url,params=params)

        response = None
        try:
            if method.upper() == 'GET':
                response = self.request_session.get(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'POST':
                response = self.request_session.post(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'PUT':
                response = self.request_session.put(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'DELETE':
                response = self.request_session.delete(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            if response is None:
                raise UnknownError(reason="Something went wrong..")

        except requests.exceptions.Timeout as e:
            raise TimeoutError(e)
        operation_status_switcher = {
            401: ExpiredSession,
            409: Conflict,
            429: TooManyRequests,
            458: Captcha, # todo handle this someday
            461: PermissionDenied,
            460: PermissionDenied,
            494: MarketLocked,
            512: TemporaryBanned,
            521: TemporaryBanned,
            478: NoTradeExistingError

        }
        if not response.ok:
            raise operation_status_switcher.get(response.status_code,UnknownError(response.content))()
        if response.text == '': response = {}
        else: response = response.json()
        if 'credits' in response and response['credits']:
            self.credits = response['credits']
        if 'duplicateItemIdList' in response:
            self.duplicates = [i['itemId'] for i in response['duplicateItemIdList']]
        return response
