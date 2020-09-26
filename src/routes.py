from .api import *


def register_routes(app):
    app.register_blueprint(app_users, url_prefix="/api/accounts")
    app.register_blueprint(ea_accounts, url_prefix="/api/accounts")
    # app.register_blueprint(players, url_prefix="/api/players")
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(web_app, url_prefix="/api/web-app")
