import re

import requests
from requests.cookies import cookiejar_from_dict

from consts import REQUEST_TIMEOUT, WEB_APP_AUTH, REDIRECT_URI_WEB_APP, EA_WEB_APP_URL, WEB_APP_CLIENT_ID
from enums import AuthMethod
from utils.db import ea_accounts_collection
from utils.exceptions import WebAppLoginError
from utils.helper_functions import server_response


class WebAppLogin:
    __instance = None

    @staticmethod
    def get_instance():
        return WebAppLogin.__instance

    def __init__(self, email, password, platform, auth_method):
        self.email = email
        self.password = password
        self.platform = platform
        self.auth_method = auth_method
        self.request_session = requests.Session()
        self.ea_server_response = None
        self.entered_correct_creadentials = False
        WebAppLogin.__instance = self

    def verify_client(self):
        """
                     todo: check if user has cookies in the ea_account collection already /
                        if he has:take it
                        if not: save the result from the get as an object not as an array
                    """
        try:
            user = ea_accounts_collection.find_one({"email": self.email})

            if not user:
                raise WebAppLoginError(reason='user does not exist')
            user_cookies = user["cookies"]

            if user_cookies:
                self.request_session.cookies = cookiejar_from_dict(user_cookies)
                self.entered_correct_creadentials = True
                return server_response(status='user identity verified', verification_method=False)
            else:
                self._navigate_to_login_page()
                self._check_if_correct_credentials()
                self.entered_correct_creadentials = True
                return server_response(status="verified credentials, waiting for status code", verification_method=True)

        except WebAppLoginError as e:
            return server_response(error=e.reason, code=401)

    def get_verification_code(self):
        self._send_verification_code_to_client()
        return server_response(status=f'verification code sent via {str(self.auth_method).lower()}')

    def set_verification_code(self, code):
        return code

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

    def _check_if_correct_credentials(self):
        if "'successfulLogin': false" in self.ea_server_response.text:
            # Your credentials are incorrect or have expired. Please try again or reset your password.
            failedReason = re.search('general-error">\s+<div>\s+<div>\s+(.*)\s.+', self.ea_server_response.text).group(1)
            self.entered_correct_creadentials = False
            raise WebAppLoginError(reason=failedReason)

    def _send_verification_code_to_client(self):
        if 'var redirectUri' in self.ea_server_response.text:
            self.ea_server_response = self.request_session.get(self.ea_server_response.url, params={'_eventId': 'end'})  # initref param was missing here

        if 'Login Verification' in self.ea_server_response.text:  # click button to get code sent
            if AuthMethod(self.auth_method) == AuthMethod.SMS:
                pass
                # self.ea_server_response = self.request_session.post(self.ea_server_response.url, {'_eventId': 'submit', 'codeType': 'SMS'})
            else:  # email
                self.ea_server_response = self.request_session.post(self.ea_server_response.url, {'_eventId': 'submit', 'codeType': 'EMAIL'})
        else:
            raise WebAppLoginError(reason='failed to send verification code')
