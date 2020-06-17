from requests.exceptions import Timeout as BaseTimeout


class FutError(RuntimeError):
    """There was an ambiguous exception that occurred while handling
    your request."""

    def __init__(self, code=None, reason=None, string=None):
        self.code = code
        self.reason = reason
        self.string = string


class TimeoutError(BaseTimeout):
    """Request timeout, looks like ea servers are down."""


class WebAppLoginError(FutError):
    """error during login to web app"""


class WebAppVerificationRequired(FutError):
    """ verification code is sent to the client to verify his identity"""


class WebAppPinEventChanged(FutError):
    """ structure of pin event has changed. High risk for ban, we suggest waiting for an update before using the app"""


class WebAppMaintenance(FutError):
    """ webapp is not available due to maintenance"""


class UnknownError(FutError):
    """Unknown error, please report full log at
    https://github.com/oczkers/fut/issues/24"""


class NoTradeExistingError(FutError):
    """[478] NO_TRADE_EXISTS (fut)
    when you bid on an item that has already been sold or the trade id isn't valid."""


class ExpiredSession(FutError):
    """Session has expired,
    you should send at least one request every ~10 minutes."""


class MaxSessions(FutError):
    """[503] Service Unavailable (ut) - max session."""


class InternalServerError(FutError):
    """[500] Internal Server Error (ut). (invalid parameters?)"""


class MarketLocked(FutError):
    """[494] If this is a new account, you need to unlock the transfer market
    by playing games and completing the starter objectives.
    If this is an older account, you may be banned from using the transfer market on the web app."""


class FeatureDisabled(FutError):
    """[480] Feature Disabled."""


class NoUltimateTeam(FutError):
    """[465] No Ultimate Team."""


class PermissionDenied(FutError):
    """[461] Permission Denied. (outbid?)"""


class Captcha(FutError):
    """[459] Captcha Triggered."""

    def __init__(self, code=None, reason=None, string=None, token=None, img=None):
        self.code = code
        self.reason = reason
        self.string = string
        self.token = token
        self.img = img

class TooManyRequests(FutError):
    """[429] Conflict. item belongs to someone else"""

class Conflict(FutError):
    """[409] Conflict. item belongs to someone else"""


class TemporaryBanned(FutError):
    """[512/521] Conflict. item belongs to someone else"""