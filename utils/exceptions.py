from requests.exceptions import Timeout as BaseTimeout


class FutError(RuntimeError):
    """There was an ambiguous exception that occurred while handling
    your request."""

    def __init__(self, code=None, reason=None, string=None):
        self.code = code
        self.reason = reason
        self.string = string


class TimeoutError(FutError, BaseTimeout):
    def __init__(self):
        self.reason = "Request timeout, looks like ea servers are down"


class WebAppLoginError(FutError):
    def __init__(self, code, reason="error during login to web app"):
        self.reason = reason
        self.code = code

class UserNotFound(BaseException):
    def __init__(self):
        self.reason = "The user doesn't exist"

class WebAppVerificationRequired(FutError):
    def __init__(self):
        self.reason = "verification code is sent to the client to verify his identity"


class WebAppPinEventChanged(FutError):
    def __init__(self):
        self.reason = "structure of pin event has changed. High risk for ban, we suggest waiting for an update before using the app"


class WebAppMaintenance(FutError):
    def __init__(self):
        self.reason = "web app is not available due to maintenance"


class UnknownError(FutError):
    def __init__(self):
        self.reason = "Unknown error occured, try and log in again"


class NoTradeExistingError(FutError):
    # [478]
    def __init__(self):
        self.reason = "Probably you bided on item that has already been sold or the trade id isn't valid"


class ExpiredSession(FutError):
    def __init__(self):
        self.reason = "Session has expired"


class MaxSessions(FutError):
    # [503]
    def __init__(self):
        self.reason = "Service Unavailable (ut) - max session"


class InternalServerError(FutError):
    # [500]
    def __init__(self):
        self.reason = "Internal server error (invalid parameters?)"


class MarketLocked(FutError):
    # [494]
    def __init__(self):
        self.reason = "Transfer market is probably disabled on this account"


class PermissionDenied(FutError):
    # [461]
    def __init__(self):
        self.reason = "Permission denied"


class Captcha(FutError):
    """[459] Captcha Triggered."""

    def __init__(self, code=None, reason=None, string=None, token=None, img=None):
        self.code = code
        self.reason = reason
        self.string = string
        self.token = token
        self.img = img


class TooManyRequests(FutError):
    # [429]
    def __init__(self):
        self.reason = "Too many requests"


class Conflict(FutError):
    # [409]
    def __init__(self):
        self.reason = "Conflict. item belongs to someone else"


class TemporaryBanned(FutError):
    # [512/521]
    def __init__(self):
        self.reason = "Temporary ban"


class NoBudgetLeft(FutError):
    def __init__(self):
        self.reason = "You have no more coins left"

class LoadingWebApp(Exception):
    pass

class AuthCodeRequired(Exception):
    def __init__(self):
        self.reason = "Auth code is required"