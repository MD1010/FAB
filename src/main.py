# import eventlet
# eventlet.monkey_patch()
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from consts import APP_SECRET_KEY
from consts import SERVER_IP
from src.api.routes import register_routes
from utils import Socket

if __name__ == '__main__':
    print(1)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = APP_SECRET_KEY

    JWTManager(app)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['JSON_SORT_KEYS'] = False
    app.config['transports'] = 'websocket'
    socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

    Socket.socket = socketio
    register_routes(app)


    socketio.run(app, port=5000, host=SERVER_IP,debug=True)
