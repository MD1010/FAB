import copy
import json
import re
from http.cookiejar import Cookie

import bcrypt
import requests
from Naked.toolshed.shell import muterun_js

from consts import REQUEST_TIMEOUT, WEB_APP_AUTH, REDIRECT_URI_WEB_APP, EA_WEB_APP_URL, \
    headers, PRE_GAME_SKU, PRE_SKU, CONFIG_URL, CONTENT_URL, GUID, YEAR, CONFIG_JSON_SUFFIX, PIN_DICT, PIDS_ME_URL, FUT_HOST, SHARDS_V2, GAME_URL, \
    ACOUNTS_INFO, ROOT_URL, DS_JS_PATH, CLIENT_VERSION
from enums import AuthMethod, Platform
from utils.db import ea_accounts_collection
from utils.exceptions import WebAppLoginError, WebAppVerificationRequired, WebAppPinEventChanged, WebAppMaintenance
from utils.helper_functions import server_response


class WebAppLogin:
    __instance = None

    @staticmethod
    def get_instance():
        return WebAppLogin.__instance

    def __init__(self, email, password, platform):
        # account
        self.email = email
        self.password = password
        self.platform = platform
        self.sku = None
        self.game_sku = None
        self.nucleus_id = None  # client pid
        self.dob = None
        self.persona_id = None

        # web app
        self.auth_url = None
        self.pin_url = None
        self.client_id = None  # FIFA-20-WEBCLIENT
        self.release_type = None
        self.fun_captcha_public_key = None
        self.fut_host = FUT_HOST[platform]

        # auth
        self.request_session = requests.Session()
        self.ea_server_response = None
        self.db_user = None
        self.entered_correct_creadentials = False
        self.access_token = None
        self.token_type = None
        self.sid = None

        WebAppLogin.__instance = self
        self.pre_login()

    def pre_login(self):
        try:
            self._initialize_webapp_config()
            if self.ea_server_response["futweb_maintenance"]:
                raise WebAppMaintenance(reason="Webapp is not available due to maintenance")
        except WebAppPinEventChanged as e:
            return server_response(error=e.reason, code=503)

    def launch_webapp(self):
        try:
            self._verify_client()
            return self._get_client_session()

        except WebAppLoginError as e:
            return server_response(error=e.reason, code=401)

        except WebAppVerificationRequired:
            return server_response(status="verified credentials, waiting for status code", verification_method=True)

    def get_verification_code(self, auth_method):
        self._send_verification_code_to_client(auth_method)
        return server_response(status=f'Verification code sent via {str(auth_method).lower()}')

    def continue_login_with_status_code(self, code):
        # todo: check maybe some conditions are not necessarry
        if 'Enter your security code' in self.ea_server_response.text:
            self.request_session.headers['Referer'] = url = self.ea_server_response.url
            self.ea_server_response = self.request_session.post(url.replace('s3', 's4'),
                                                                {'oneTimeCode': code,
                                                                 '_trustThisDevice': 'on',
                                                                 '_eventId': 'submit'},
                                                                timeout=REQUEST_TIMEOUT)
            if 'Incorrect code entered' in self.ea_server_response.text or 'Please enter a valid security code' in self.ea_server_response.text:
                return server_response(error="provided code is incorrect", code=401)
            # if 'Set Up an App Authenticator' in self.ea_server_response.text:
            #     self.ea_server_response = self.request_session.post(url.replace('s3', 's4'), {'_eventId': 'cancel', 'appDevice': 'IPHONE'},
            #                                    timeout=REQUEST_TIMEOUT)
        self._set_access_token_first_time()
        self._save_cookies()
        return self.launch_webapp()

    # private functions in order
    def _initialize_webapp_config(self):
        self.ea_server_response = self.request_session.get(CONFIG_URL).json()
        self.auth_url = self.ea_server_response['authURL']  # utas.mob.v2.fut.ea.com:443
        self.pin_url = self.ea_server_response['pinURL']  # https://pin-river.data.ea.com/pinEvents
        self.client_id = self.ea_server_response['eadpClientId']  # FIFA-20-WEBCLIENT
        self.release_type = self.ea_server_response['releaseType']  # prod
        self.fun_captcha_public_key = self.ea_server_response['funCaptchaPublicKey']  # A4EECF77-AC87-8C8D-5754-BF882F72063B
        self.ea_server_response = self.request_session.get(f"{CONTENT_URL}/{GUID}/{YEAR}/{CONFIG_JSON_SUFFIX}").json()
        if self.ea_server_response['pin'] != PIN_DICT:
            raise WebAppPinEventChanged(reason="Structure of pin event has changed. High risk for ban, we suggest waiting for an update before using the app")

    def _verify_client(self):
        # if the user exists in db it means that he was logged in successfully previously or code was set correctly with correct credentials
        self.db_user = ea_accounts_collection.find_one({"email": self.email})
        # credential verification from db -> the user already was logged in previously so there is no point to refer to ea
        if self.db_user:
            if bcrypt.hashpw(self.password.encode('utf-8'), self.db_user["password"]) == self.db_user["password"] and self.platform == self.db_user["platform"]:
                self.entered_correct_creadentials = True
            else:
                self.entered_correct_creadentials = False
                raise WebAppLoginError(reason="Login failed, wrong credentials provided.", code=401)

        # if provided correct credentials take the cookies and launch web app
        if self.db_user.get("cookies"):
            self.request_session.cookies._cookies = self._load_cookies(self.db_user["cookies"])
        else:
            self._navigate_to_login_page()
            self._check_if_correct_credentials()
            self.entered_correct_creadentials = True
            raise WebAppVerificationRequired()

    def _navigate_to_login_page(self):
        params = {
            'prompt': 'login',
            'accessToken': 'null',
            'client_id': self.client_id,
            'response_type': 'token',
            'display': 'web2/login',
            'locale': 'en_US',
            'redirect_uri': REDIRECT_URI_WEB_APP,
            'release_type': 'prod',
            'scope': 'basic.identity offline signin'
        }
        self.request_session.headers['Referer'] = EA_WEB_APP_URL
        self.ea_server_response = self.request_session.get(WEB_APP_AUTH, params=params, timeout=REQUEST_TIMEOUT)

        if self.ea_server_response.url != REDIRECT_URI_WEB_APP:
            self.request_session.headers['Referer'] = self.ea_server_response.url
            data = {'email': self.email,
                    'password': self.password,
                    'country': 'US',
                    'phoneNumber': '',
                    'passwordForPhone': '',
                    'gCaptchaResponse': '',
                    'isPhoneNumberLogin': 'false',
                    'isIncompletePhone': '',
                    '_rememberMe': 'on',
                    'vrememberMe': 'on',
                    '_eventId': 'submit'}

            self.ea_server_response = self.request_session.post(self.ea_server_response.url,
                                                                data=data, timeout=REQUEST_TIMEOUT)

    def _check_if_correct_credentials(self):
        if "'successfulLogin': false" in self.ea_server_response.text:
            # Your credentials are incorrect or have expired. Please try again or reset your password.
            failedReason = re.search('general-error">\s+<div>\s+<div>\s+(.*)\s.+',
                                     self.ea_server_response.text).group(1)
            self.entered_correct_creadentials = False
            raise WebAppLoginError(reason=failedReason)

    def _send_verification_code_to_client(self, auth_method):
        if 'var redirectUri' in self.ea_server_response.text:
            self.ea_server_response = self.request_session.get(self.ea_server_response.url, params={'_eventId': 'end'})  # initref param was missing here
        if 'Login Verification' in self.ea_server_response.text:  # click button to get code sent
            if AuthMethod(auth_method) == AuthMethod.SMS:
                self.ea_server_response = self.request_session.post(self.ea_server_response.url,
                                                                    {'_eventId': 'submit',
                                                                     'codeType': 'SMS'})
            else:  # email
                self.ea_server_response = self.request_session.post(self.ea_server_response.url,
                                                                    {'_eventId': 'submit',
                                                                     'codeType': 'EMAIL'})
        else:
            raise WebAppLoginError(reason='failed to send verification code')

    def _set_access_token_first_time(self):
        self.ea_server_response = re.match(
            'https://www.easports.com/fifa/ultimate-team/web-app/auth.html#access_token=(.+?)&token_type=(.+?)&expires_in=[0-9]+',
            self.ea_server_response.url)
        self.access_token = self.ea_server_response.group(1)
        self.token_type = self.ea_server_response.group(2)

    def _save_cookies(self):
        # copy the cookie format to revert after save
        cookies_in_Cookie_format = copy.deepcopy(self.request_session.cookies._cookies)
        for domain in self.request_session.cookies._cookies:
            for path in self.request_session.cookies._cookies[domain]:
                for cookie in self.request_session.cookies._cookies[domain][path]:
                    self.request_session.cookies._cookies[domain][path][cookie] = \
                        self.request_session.cookies._cookies[domain][path][cookie].__dict__
        ea_accounts_collection.update_one({"email": self.email}, {
            "$set": {"cookies": self.request_session.cookies._cookies, "platform": self.platform}})
        # convert back to Cookie Format from dict
        self.request_session.cookies._cookies = cookies_in_Cookie_format

    def _load_cookies(self, user_cookies):
        for domain in user_cookies:
            for path in user_cookies[domain]:
                for cookie in user_cookies[domain][path]:
                    version = user_cookies[domain][path][cookie].get("version")
                    name = user_cookies[domain][path][cookie].get("name")
                    value = user_cookies[domain][path][cookie].get("value")
                    port = user_cookies[domain][path][cookie].get("port")
                    port_specified = user_cookies[domain][path][cookie].get("port_specified")
                    domain = user_cookies[domain][path][cookie].get("domain")
                    domain_specified = user_cookies[domain][path][cookie].get("domain_specified")
                    domain_initial_dot = user_cookies[domain][path][cookie].get("domain_initial_dot")
                    path = user_cookies[domain][path][cookie].get("path")
                    path_specified = user_cookies[domain][path][cookie].get("path_specified")
                    secure = user_cookies[domain][path][cookie].get("secure")
                    expires = user_cookies[domain][path][cookie].get("expires")
                    discard = user_cookies[domain][path][cookie].get("discard")
                    comment = user_cookies[domain][path][cookie].get("comment")
                    comment_url = user_cookies[domain][path][cookie].get("comment_url")
                    rest = user_cookies[domain][path][cookie].get("_rest")
                    user_cookies[domain][path][cookie] = Cookie(version, name, value, port,
                                                                port_specified, domain,
                                                                domain_specified,
                                                                domain_initial_dot, path,
                                                                path_specified, secure, expires,
                                                                discard, comment, comment_url,
                                                                rest)
        return user_cookies

    def _get_client_session(self):
        self.request_session.headers = headers.copy()
        self._determine_game_sku()
        # todo: check whitch PIN EVENT is sent here!
        self._update_access_token()
        self._get_additional_account_data()
        self._check_if_persona_found()
        self._finish_authoriztion_and_get_sid()
        return self._save_sid_if_success()

    def _determine_game_sku(self):
        if Platform(self.platform) == Platform.pc:
            self.game_sku = f'{PRE_GAME_SKU}PCC'
        elif Platform(self.platform) == Platform.xbox:
            self.game_sku = f'{PRE_GAME_SKU}XBO'
        elif Platform(self.platform) == Platform.xbox360:
            self.game_sku = f'{PRE_GAME_SKU}XBX'
        elif Platform(self.platform) == Platform.ps3:
            self.game_sku = f'{PRE_GAME_SKU}PS3'
        elif Platform(self.platform) == Platform.ps4:
            self.game_sku = f'{PRE_GAME_SKU}PS4'
        self.sku = f'{PRE_SKU}WEB'

    def _update_access_token(self):
        params = {'accessToken': self.access_token,
                  'client_id': self.client_id,
                  'response_type': 'token',
                  'release_type': 'prod',
                  'display': 'web2/login',
                  'locale': 'en_US',
                  'redirect_uri': REDIRECT_URI_WEB_APP,
                  'scope': 'basic.identity offline signin'}
        self.ea_server_response = self.request_session.get(WEB_APP_AUTH, params=params)
        self.ea_server_response = re.match(f'{REDIRECT_URI_WEB_APP}#access_token=(.+?)&token_type=(.+?)&expires_in=[0-9]+', self.ea_server_response.url)
        # remid cookie expired
        if self.ea_server_response is None:
            # delete the expired cookies
            ea_accounts_collection.update_one({"email": self.email}, {
                "$set": {"cookies": {}, "platform": self.platform}})
            raise WebAppVerificationRequired()
        self.access_token = self.ea_server_response.group(1)
        self.token_type = self.ea_server_response.group(2)

    def _get_additional_account_data(self):
        self.ea_server_response = self.request_session.get(EA_WEB_APP_URL, timeout=REQUEST_TIMEOUT).text
        self.request_session.headers['Referer'] = EA_WEB_APP_URL
        self.request_session.headers['Accept'] = 'application/json'
        self.request_session.headers['Authorization'] = f'{self.token_type} {self.access_token}'
        self.ea_server_response = self.request_session.get(PIDS_ME_URL).json()
        # this check is not needed ???
        if self.ea_server_response.get('error') == 'invalid_access_token':
            raise WebAppLoginError(reason="invalid access token")
        self.nucleus_id = self.ea_server_response['pid']['externalRefValue']
        self.dob = self.ea_server_response['pid']['dob']
        del self.request_session.headers['Authorization']
        self.request_session.headers['Easw-Session-Data-Nucleus-Id'] = self.nucleus_id
        # shards
        self.ea_server_response = self.request_session.get(f'https://{self.auth_url}/{SHARDS_V2}').json()

    def _check_if_persona_found(self):
        data = {'filterConsoleLogin': 'true',
                'sku': self.sku,
                'returningUserGameYear': YEAR - 1}
        self.ea_server_response = self.request_session.get(f'https://{self.fut_host}/{GAME_URL}/{ACOUNTS_INFO}', params=data).json()
        # find persona
        personas = self.ea_server_response['userAccountInfo']['personas']
        for p in personas:
            for c in p['userClubList']:
                if c['skuAccessList'] and self.game_sku in c['skuAccessList']:
                    self.persona_id = p['personaId']
                    break
        if not self.persona_id:
            raise WebAppLoginError(reason="No persona found - wrong credentials provided.")

    def _generate_ds(self, auth_code):
        ds = auth_code + " " + self.sku + " " + self.access_token
        return str(muterun_js(DS_JS_PATH, ds).stdout)[2:-3]

    def _finish_authoriztion_and_get_sid(self):
        del self.request_session.headers['Easw-Session-Data-Nucleus-Id']
        self.request_session.headers['Origin'] = ROOT_URL
        params = {'client_id': 'FOS-SERVER',
                  'redirect_uri': 'nucleus:rest',
                  'response_type': 'code',
                  'access_token': self.access_token,
                  'release_type': 'prod'}
        res = self.ea_server_response = self.request_session.get(WEB_APP_AUTH, params=params).json()
        auth_code = res['code']

        # ds algorithm
        ds = self._generate_ds(auth_code)
        self.request_session.headers['Content-Type'] = 'application/json'
        data = {'isReadOnly': 'false',
                'sku': self.sku,
                'clientVersion': CLIENT_VERSION,
                'nucleusPersonaId': self.persona_id,
                'gameSku': self.game_sku,
                'locale': 'en-US',
                'method': 'authcode',
                'priorityLevel': 4,
                'identification': {'authCode': auth_code,
                                   'redirectUrl': 'nucleus:rest'},
                'ds': ds}
        self.ea_server_response = self.request_session.post(f'https://{self.fut_host}/ut/auth', data=json.dumps(data),
                                                            timeout=REQUEST_TIMEOUT)

    def _save_sid_if_success(self):
        if self.ea_server_response.status_code == 401:  # and rc.text == 'multiple session'
            raise WebAppLoginError(reason='Multiple session')
        if self.ea_server_response.status_code == 500:
            raise WebAppLoginError(reason='Servers are probably temporary down.')
        if self.ea_server_response.status_code == 458:
            raise WebAppLoginError(reason='Fun Captcha found. Go to webapp and solve it, then log in again.')
        if self.ea_server_response.status_code == 403:
            raise WebAppLoginError(reason='Server returned Forbiden. Probably you have not received access to web app')
        self.ea_server_response = self.ea_server_response.json()
        if self.ea_server_response.get('reason'):
            raise WebAppLoginError(reason=self.ea_server_response.get('reason'))

        self.request_session.headers['X-UT-SID'] = self.sid = self.ea_server_response['sid']
        self.request_session.headers['Easw-Session-Data-Nucleus-Id'] = self.nucleus_id
        return server_response(auth=self.ea_server_response)
