from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from api.app_users import app_users
from api.auth import auth
from api.ea_accounts import ea_accounts
from api.players import players
from consts.app import *

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['transports'] = 'websocket'
app.config['JSON_SORT_KEYS'] = False
socketio = SocketIO(app, async_mode='threading')

# register app routes
app.register_blueprint(app_users, url_prefix="/api/users")
app.register_blueprint(ea_accounts, url_prefix="/api/accounts")
app.register_blueprint(players, url_prefix="/api/players")
app.register_blueprint(auth, url_prefix="/auth")

if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    socketio.run(app, host="0.0.0.0", debug=True)
