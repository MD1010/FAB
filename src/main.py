from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from consts import APP_SECRET_KEY, SERVER_IP
from src.events import initSocketEvents
from src.routes import register_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['transports'] = 'websocket'
app.config['JSON_SORT_KEYS'] = False
socketio = SocketIO(app, cors_allowed_origins="*")

register_routes(app)
initSocketEvents(socketio)

if __name__ == '__main__':
    socketio.run(app, host=SERVER_IP, debug=True)
