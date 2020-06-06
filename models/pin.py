import json
import time
from datetime import datetime
from random import random

import requests

from consts import APP_VERSION, headers, ROOT_URL, EA_WEB_APP_URL
from consts.pin_events import TAXV, TIDT, REL, GID, PLAT, ET, PIDT, PIN_URL
from utils.exceptions import WebAppPinEventChanged


class Pin(object):
    def __init__(self, sku=None, sid='', nucleus_id=0, persona_id='', dob=False, platform=False):
        self.sid = sid
        self.nucleus_id = nucleus_id
        self.persona_id = persona_id
        self.dob = dob
        self.platform = platform
        self.sku = sku

        # sent in pin events
        self.taxv = TAXV
        self.tidt = TIDT
        self.rel = REL
        self.gid = GID
        self.plat = PLAT
        self.et = ET
        self.pidt = PIDT
        self.v = APP_VERSION
        self.s = 2  # 2 were sent and omitted

        self.r = requests.Session()
        self.r.headers = headers
        self.r.headers['Origin'] = ROOT_URL
        self.r.headers['Referer'] = EA_WEB_APP_URL
        self.r.headers['x-ea-game-id'] = self.sku
        self.r.headers['x-ea-game-id-type'] = self.tidt
        self.r.headers['x-ea-taxv'] = self.taxv

        self.custom = {"networkAccess": "G", 'service_plat': platform[:3]}

    # timestamp
    @property
    def __ts(self):
        ts = datetime.utcnow()
        ts = ts.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return ts

    def generate_event(self, en, pgid=False, status=False, source=False, end_reason=False):  # type=False
        data = {
            "core": {
                "en": en,
                "pid": self.persona_id,
                "pidm": {"nucleus": self.nucleus_id},
                "pidt": self.pidt,
                "s": self.s,
                "ts_event": self.__ts
            }
        }
        # todo: maybe not needed?
        if self.dob:  # date of birth yyyy-mm
            data['core']['dob'] = self.dob
        if pgid:
            data['pgid'] = pgid
        if status:
            data['status'] = status
        if source:
            data['source'] = source
        if end_reason:
            data['end_reason'] = end_reason
        if en == 'login':
            data['type'] = 'utas'
            data['userid'] = self.persona_id
        elif en == 'page_view':
            data['type'] = 'menu'
        elif en == 'error':
            data['server_type'] = 'utas'
            data['errid'] = 'server_error'
            data['type'] = 'disconnect'
            data['sid'] = self.sid

        self.s += 1  # bump event id
        return data

    def send_pin(self, events, fast=False):
        time.sleep(0.5 + random() / 50)
        data = {
            "custom": self.custom,
            "et": self.et,
            "events": events,
            "gid": self.gid,
            "is_sess": self.sid != '',
            "loc": "en_US",
            "plat": self.plat,
            "rel": self.rel,
            "sid": self.sid,
            "taxv": self.taxv,
            "tid": self.sku,
            "tidt": self.tidt,
            "ts_post": self.__ts,
            "v": self.v
        }
        # print(data)  # DEBUG
        if not fast:
            self.r.options(PIN_URL)
        rc = self.r.post(PIN_URL, data=json.dumps(data)).json()
        if rc['status'] != 'ok':
            raise WebAppPinEventChanged(reason='PinEvent is NOT OK, probably they changed something.')
        return True
