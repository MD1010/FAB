import re

import requests
from requests.cookies import cookiejar_from_dict

from consts.app import WEB_APP_CLIENT_ID, REDIRECT_URI_WEB_APP, EA_WEB_APP_URL, WEB_APP_AUTH, REQUEST_TIMEOUT
from enums.auth_method import AuthMethod
from utils.db import ea_accounts_collection
from utils.helper_functions import server_response


class WebAppLogin:
    def __init__(self, email, password, platform, auth_method):
        self.email = email
        self.password = password
        self.platform = platform
        self.auth_method = auth_method
        self.request_session = requests.Session()
        self.ea_server_response = None

    def launch_web_app(self):
        """
         todo: check if user has cookies in the ea_account collection already /
            if he has:take it
            if not: save the result from the get as an object not as an array
        """

        user_cookies = ea_accounts_collection.find_one({"email": self.email})["cookies"]
        if user_cookies:
            self.request_session.cookies = cookiejar_from_dict(user_cookies)
        else:
            self._login_first_time()
        return server_response(web_app_status="successfully logged in")

    def _login_first_time(self):

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

        self.ea_server_response = self.request_session.get(WEB_APP_AUTH, params=params, headers=headers, timeout=REQUEST_TIMEOUT)

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
                    'rememberMe': 'on',
                    '_eventId': 'submit'}

            self.ea_server_response = self.request_session.post(self.ea_server_response.url, data=data, timeout=REQUEST_TIMEOUT)

            if "'successfulLogin': false" in self.ea_server_response.text:
                # Your credentials are incorrect or have expired. Please try again or reset your password.
                failedReason = re.search('general-error">\s+<div>\s+<div>\s+(.*)\s.+', self.ea_server_response.text).group(1)
                return server_response(web_app_status=failedReason, code=401)

            if 'var redirectUri' in self.ea_server_response.text:
                self.ea_server_response = self.request_session.get(self.ea_server_response.url, params={'_eventId': 'end'})  # initref param was missing here

            if 'Login Verification' in self.ea_server_response.text:  # click button to get code sent
                if AuthMethod(self.auth_method) == AuthMethod.SMS:
                    pass
                    # self.ea_server_response = self.request_session.post(self.ea_server_response.url, {'_eventId': 'submit', 'codeType': 'SMS'})
                else:  # email
                    self.ea_server_response = self.request_session.post(self.ea_server_response.url, {'_eventId': 'submit', 'codeType': 'EMAIL'})
