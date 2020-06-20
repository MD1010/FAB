import json
import time
from random import random

import requests

from consts import GAME_URL, REQUEST_TIMEOUT
from models.pin import WebAppEvent
from src.auth.live_logins import authenticated_accounts
from utils.exceptions import TimeoutError, UnknownError, ExpiredSession, Conflict, TooManyRequests, Captcha, PermissionDenied, MarketLocked, TemporaryBanned, \
    NoTradeExistingError


# this class will be vreated ouside the fab loop -> the decorator of the /start-fab will insure that the account is authenticated
from utils.helper_functions import send_pin_event


class WebappActions:
    def __init__(self, ea_account):
        self.login_instance = authenticated_accounts.get(ea_account)
        self.host = self.login_instance.fut_host
        self.request_session = self.login_instance.request_session
        self.pin = self.login_instance.pin
        self.request_count = 0
        self.credits = 0
        self.duplicates = 0

    def _webapp_request(self, method, url, data=None, params=None):
        self.request_count += 1
        data = data or {}
        params = params or {}
        url = f'https://{self.host}/{GAME_URL}/{url}'
        # respect min wait time between requests
        time.sleep(random.unform(1.1, 2.5))
        self.request_session.options(url, params=params)

        res = None
        try:
            if method.upper() == 'GET':
                res = self.request_session.get(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'POST':
                res = self.request_session.post(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'PUT':
                res = self.request_session.put(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            elif method.upper() == 'DELETE':
                res = self.request_session.delete(url, data=data, params=params, timeout=REQUEST_TIMEOUT)
            if res is None:
                raise UnknownError(reason="Something went wrong..")

        except requests.exceptions.Timeout as e:
            raise TimeoutError(e)
        operation_status_switcher = {
            401: ExpiredSession,
            409: Conflict,
            429: TooManyRequests,
            458: Captcha,  # todo handle this someday
            461: PermissionDenied,
            460: PermissionDenied,
            494: MarketLocked,
            512: TemporaryBanned,
            521: TemporaryBanned,
            478: NoTradeExistingError

        }
        if not res.ok:
            raise operation_status_switcher.get(res.status_code, UnknownError(res.content))()
        if res.text == '':
            res = {}
        else:
            res = res.json()
        if 'credits' in res and res['credits']:
            self.credits = res['credits']
        if 'duplicateItemIdList' in res:
            self.duplicates = [i['itemId'] for i in res['duplicateItemIdList']]
        return res

    def sendToPile(self, pile, item_id=None):
        if not isinstance(item_id, (list, tuple)):
            item_id = (item_id,)
        data = {"itemData": [{'pile': pile, 'id': i} for i in item_id]}

        res = self._webapp_request('PUT', 'item', data=json.dumps(data))

        if res['itemData'][0]['success']:
            """ emit here from socket io that the item was sent """
            print(f"item {item_id} was sent to transfer list")
        else:
            print(f"failed to list item, reason: { res['itemData'][0]['reason']}")

    def search_items(self, ctype, level=None, category=None, assetId=None, defId=None,
                     min_price=None, max_price=None, min_buy=None, max_buy=None,
                     league=None, club=None, position=None, zone=None, nationality=None,
                     rare=False, playStyle=None, start=0, page_size=itemsPerPage['transferMarket'],
                     fast=False):
        """Prepare search request, send and return parsed data as a dict.

        :param ctype: player/training
        :param level: (optional) Card level.
        :param category: (optional) [fitness/?/?] Card category.
        :param assetId: (optional) Asset id.
        :param defId: (optional) Definition id.
        :param min_price: (optional) Minimal price.
        :param max_price: (optional) Maximum price.
        :param min_buy: (optional) Minimal buy now price.
        :param max_buy: (optional) Maximum buy now price.
        :param league: (optional) League id.
        :param club: (optional) Club id.
        :param position: (optional) Position.
        :param nationality: (optional) Nation id.
        :param rare: (optional) [boolean] True for searching special cards.
        :param playStyle: (optional) Play style.
        :param start: (optional) Start page sent to server so it supposed to be 12/15, 24/30 etc. (default platform page_size*n)
        :param page_size: (optional) Page size (items per page).
        """

        # pinEvents
        if start == 0:
            send_pin_event(self.pin, [
                WebAppEvent('page_view', pgid='Hub - Transfers'),
                WebAppEvent('page_view', pgid='Transfer Market Search')
            ])

        params = {
            'start': start,
            'num': page_size,
            'type': ctype,  # "type" namespace is reserved in python
        }
        if level:
            params['lev'] = level
        if category:
            params['cat'] = category
        if assetId:
            params['maskedDefId'] = assetId
        if defId:
            params['definitionId'] = defId
        if min_price:
            params['micr'] = min_price
        if max_price:
            params['macr'] = max_price
        if min_buy:
            params['minb'] = min_buy
        if max_buy:
            params['maxb'] = max_buy
        if league:
            params['leag'] = league
        if club:
            params['team'] = club
        if position:
            params['pos'] = position
        if zone:
            params['zone'] = zone
        if nationality:
            params['nat'] = nationality
        if rare:
            params['rare'] = 'SP'
        if playStyle:
            params['playStyle'] = playStyle

        rc = self._webapp_request('GET', 'transfermarket', params=params)

        # pinEvents
        if start == 0:
            events = [self.pin.event('page_view', 'Transfer Market Results - List View'), self.pin.event('page_view', 'Item - Detail View')]
            self.pin.send(events, fast=fast)

        # return [itemParse(i) for i in rc.get('auctionInfo', ())]

    def logout(self):
        self.request_session.delete(f'https://{self.host}/ut/auth' , timeout=REQUEST_TIMEOUT)

