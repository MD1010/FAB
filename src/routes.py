from src.api.webapp_login import login
from src.api.webapp_actions import actions
from src.api.app_users import app_users
from src.api.auth import auth
from src.api.ea_accounts import ea_accounts
from src.api.players import players
from src.api.webapp import webapp


def register_routes(app):
    app.register_blueprint(app_users, url_prefix="/api/accounts")
    app.register_blueprint(ea_accounts, url_prefix="/api/accounts")
    app.register_blueprint(players, url_prefix="/api/players")
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(webapp, url_prefix="/api/webapp")
