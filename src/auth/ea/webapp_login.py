import re
from http.cookiejar import Cookie, LWPCookieJar

import requests

from consts import REQUEST_TIMEOUT, WEB_APP_AUTH, REDIRECT_URI_WEB_APP, EA_WEB_APP_URL, \
    WEB_APP_CLIENT_ID, headers, PRE_GAME_SKU, PRE_SKU, CONFIG_URL, CONTENT_URL, GUID, YEAR, CONFIG_JSON_SUFFIX, PIN_DICT
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

        # web app
        self.authURL = None
        self.pin_url = None
        self.client_id = None
        self.release_type = None
        self.fun_captcha_public_key = None

        # auth
        self.request_session = requests.Session()
        self.request_session.cookies = LWPCookieJar()
        self.ea_server_response = None
        self.entered_correct_creadentials = False
        self.access_token = None
        self.token_type = None

        WebAppLogin.__instance = self
        self.pre_login()

    def pre_login(self):
        try:
            self._initialize_webapp_config()
            if self.ea_server_response["futweb_maintenance"]:
                raise WebAppMaintenance(reason="webapp is not available due to maintenance")
        except WebAppPinEventChanged as e:
            return server_response(error=e.reason, code=503)

    def launch_webapp(self):
        try:
            self._verify_client()
            self._get_client_session()

        except WebAppLoginError as e:
            return server_response(error=e.reason, code=401)

        except WebAppVerificationRequired:
            return server_response(status="verified credentials, waiting for status code",
                                   verification_method=True)

    def get_verification_code(self, auth_method):
        self._send_verification_code_to_client(auth_method)
        return server_response(status=f'verification code sent via {str(auth_method).lower()}')

    def continue_login_with_status_code(self, code):
        # todo: check maybe some conditions are not necessarry
        if 'Enter your security code' in self.ea_server_response.text:
            self.request_session.headers = url = self.ea_server_response.url
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
            self.launch_webapp()

    # private functions in order
    def _initialize_webapp_config(self):
        self.ea_server_response = self.request_session.get(CONFIG_URL).json()
        self.authURL = self.ea_server_response['authURL']
        self.pin_url = self.ea_server_response['pinURL']
        self.client_id = self.ea_server_response['eadpClientId']
        self.release_type = self.ea_server_response['releaseType']
        self.fun_captcha_public_key = self.ea_server_response['funCaptchaPublicKey']
        self.ea_server_response = self.request_session.get(f"{CONTENT_URL}/{GUID}/{YEAR}/{CONFIG_JSON_SUFFIX}").json()
        if self.ea_server_response['pin'] != PIN_DICT:
            raise WebAppPinEventChanged(reason="structure of pin event has changed. High risk for ban, we suggest waiting for an update before using the app")

    def _verify_client(self):
        # already verified - enters here again after successfull status code
        if self.entered_correct_creadentials: return

        user = ea_accounts_collection.find_one({"email": self.email})

        if not user:
            raise WebAppLoginError(reason='user does not exist')

        user_cookies = user["cookies"]
        if user_cookies:
            self.request_session.cookies._cookies = self._load_cookies(user_cookies)
            self.entered_correct_creadentials = True
        else:
            self._navigate_to_login_page()
            self._check_if_correct_credentials()
            self.entered_correct_creadentials = True
            raise WebAppVerificationRequired()

    def _navigate_to_login_page(self):
        params = {
            'prompt': 'login',
            'accessToken': '',
            'client_id': WEB_APP_CLIENT_ID,
            'response_type': 'token',
            'display': 'web2/login',
            'locale': 'en_US',
            'redirect_uri': REDIRECT_URI_WEB_APP,
            'release_type': 'prod',
            'scope': 'basic.identity offline signin'
        }
        headers = {
            'Referer': EA_WEB_APP_URL
        }

        self.ea_server_response = self.request_session.get(WEB_APP_AUTH, params=params,
                                                           headers=headers, timeout=REQUEST_TIMEOUT)

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
            self.ea_server_response = self.request_session.get(self.ea_server_response.url, params={
                '_eventId': 'end'})  # initref param was missing here
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
        rc = re.match(
            'https://www.easports.com/fifa/ultimate-team/web-app/auth.html#access_token=(.+?)&token_type=(.+?)&expires_in=[0-9]+',
            self.ea_server_response.url)
        self.access_token = rc.group(1)
        self.token_type = rc.group(2)

    def _save_cookies(self):
        for domain in self.request_session.cookies._cookies:
            for path in self.request_session.cookies._cookies[domain]:
                for cookie in self.request_session.cookies._cookies[domain][path]:
                    self.request_session.cookies._cookies[domain][path][cookie] = \
                        self.request_session.cookies._cookies[domain][path][cookie].__dict__
        ea_accounts_collection.update_one({"email": self.email}, {
            "$set": {"cookies": self.request_session.cookies._cookies}})

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
        raise WebAppLoginError(reason="Wrong Platform specified")

    def _determine_game_sku(self):
        if Platform(self.platform) == Platform.pc:
            self.game_sku = '%sPCC' % PRE_GAME_SKU
        elif Platform(self.platform) == Platform.xbox:
            self.game_skuu = '%sXBO' % PRE_GAME_SKU
        elif Platform(self.platform) == Platform.xbox360:
            self.game_sku = '%sXBX' % PRE_GAME_SKU
        elif Platform(self.platform) == Platform.ps3:
            self.game_sku = '%sPS3' % PRE_GAME_SKU
        elif Platform(self.platform) == Platform.ps4:
            self.game_sku = '%sPS4' % PRE_GAME_SKU
        self.sku = '%sWEB' % PRE_SKU

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
        self.access_token = self.ea_server_response.group(1)
        self.token_type = self.ea_server_response.group(2)

    def _get_additional_account_data(self):

