from typing import Dict, TYPE_CHECKING

# prevent cyclic imports


if TYPE_CHECKING:
    from src.auth.web_app_login import WebAppLogin
    from src.auth.selenium_login import SeleniumLogin

authenticated_accounts: Dict[str, 'WebAppLogin'] = {}

login_attempts: Dict[str, 'SeleniumLogin'] = {}
