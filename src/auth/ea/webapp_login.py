import re
from http.cookiejar import Cookie, LWPCookieJar

import requests

from consts import REQUEST_TIMEOUT, WEB_APP_AUTH, REDIRECT_URI_WEB_APP, EA_WEB_APP_URL, \
    WEB_APP_CLIENT_ID, headers
from enums import AuthMethod
from utils.db import ea_accounts_collection
from utils.exceptions import WebAppLoginError
from utils.helper_functions import server_response


class WebAppLogin:
    __instance = None

    @staticmethod
    def get_instance():
        return WebAppLogin.__instance

    def __init__(self, email, password, platform):
        self.email = email
        self.password = password
        self.platform = platform
        self.auth_method = None
        self.request_session = requests.Session()
        self.request_session.cookies = LWPCookieJar()
        self.ea_server_response = None
        self.entered_correct_creadentials = False
        self.access_token = None
        self.token_type = None
        WebAppLogin.__instance = self

    def verify_client(self):
        try:
            user = ea_accounts_collection.find_one({"email": self.email})

            if not user:
                raise WebAppLoginError(reason='user does not exist')
            user_cookies = user["cookies"]

            if user_cookies:
                self.request_session.cookies._cookies = self._load_cookies(user_cookies)
                self.entered_correct_creadentials = True
                return server_response(status='user identity verified', verification_method=False)
            else:
                self._navigate_to_login_page()
                self._check_if_correct_credentials()
                self.entered_correct_creadentials = True
                return server_response(status="verified credentials, waiting for status code",
                                       verification_method=True)

        except WebAppLoginError as e:
            return server_response(error=e.reason, code=401)

    def get_verification_code(self, auth_method):
        self.auth_method = auth_method
        self._send_verification_code_to_client()
        return server_response(status=f'verification code sent via {str(self.auth_method).lower()}')

    def set_verification_code(self, code):
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
            self._set_access_token()
            self._save_cookies()
            return server_response(status="verification code accepted", code=200)

    def launch_webapp(self):
        try:
            self.request_session.headers = headers.copy()

        except WebAppLoginError as e:
            return server_response(error=e.reason, code=401)

    def _set_access_token(self):
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

    def _send_verification_code_to_client(self):
        if 'var redirectUri' in self.ea_server_response.text:
            self.ea_server_response = self.request_session.get(self.ea_server_response.url, params={
                '_eventId': 'end'})  # initref param was missing here
        if 'Login Verification' in self.ea_server_response.text:  # click button to get code sent
            if AuthMethod(self.auth_method) == AuthMethod.SMS:
                self.ea_server_response = self.request_session.post(self.ea_server_response.url,
                                                                    {'_eventId': 'submit',
                                                                     'codeType': 'SMS'})
            else:  # email
                self.ea_server_response = self.request_session.post(self.ea_server_response.url,
                                                                    {'_eventId': 'submit',
                                                                     'codeType': 'EMAIL'})
        else:
            raise WebAppLoginError(reason='failed to send verification code')

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
