from typing import Dict,TYPE_CHECKING

# prevent cyclic imports
if TYPE_CHECKING:
    from src.auth.webapp_login import WebAppLogin

authenticated_accounts: Dict[str, 'WebAppLogin'] = {}
