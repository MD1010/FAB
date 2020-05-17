import re

import requests
from requests.cookies import cookiejar_from_dict

from consts import REQUEST_TIMEOUT, WEB_APP_AUTH, REDIRECT_URI_WEB_APP, EA_WEB_APP_URL, WEB_APP_CLIENT_ID
from enums import AuthMethod
from utils.db import ea_accounts_collection
from utils.helper_functions import server_response


class WebAppLogin:
    __instance = None

    @staticmethod
    def get_instance():
        return WebAppLogin.__instance

    def __init__(self, email, password, platform, auth_method):
        if WebAppLogin.__instance is not None:
            if WebAppLogin.__instance.email == email:
                raise Exception('Singleton already created for this email')
        self.email = email
        self.password = password
        self.platform = platform
        self.auth_method = auth_method
        self.request_session = requests.Session()
        self.ea_server_response = None
        WebAppLogin.__instance = self

    def launch_webapp(self):
        """
         todo: check if user has cookies in the ea_account collection already /
            if he has:take it
            if not: save the result from the get as an object not as an array
        """
        user = ea_accounts_collection.find_one({"email": self.email})
        if not user:
            return server_response(msg="user doesnt exist", code=401)
        user_cookies = user["cookies"]

        if user_cookies:
            self.request_session.cookies = cookiejar_from_dict(user_cookies)
        else:
            return self._login_first_time()

    def set_verification_code(self, code):
        return code

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
            return self._send_verification_code()

    def _send_verification_code(self):
        if "'successfulLogin': false" in self.ea_server_response.text:
            # Your credentials are incorrect or have expired. Please try again or reset your password.
            failedReason = re.search('general-error">\s+<div>\s+<div>\s+(.*)\s.+', self.ea_server_response.text).group(1)
            return server_response(webapp_status=failedReason, code=401)

        if 'var redirectUri' in self.ea_server_response.text:
            self.ea_server_response = self.request_session.get(self.ea_server_response.url, params={'_eventId': 'end'})  # initref param was missing here

        if 'Login Verification' in self.ea_server_response.text:  # click button to get code sent
            if AuthMethod(self.auth_method) == AuthMethod.SMS:
                self.ea_server_response = self.request_session.post(self.ea_server_response.url, {'_eventId': 'submit', 'codeType': 'SMS'})
            else:  # email
                self.ea_server_response = self.request_session.post(self.ea_server_response.url, {'_eventId': 'submit', 'codeType': 'EMAIL'})
        return server_response(webapp_status=f'verification code sent via {str(self.auth_method).lower()}')
