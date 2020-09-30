from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, join_room, leave_room

from consts import APP_SECRET_KEY, SERVER_IP
from src.routes import register_routes
from utils.helper_functions import server_response

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
JWTManager(app)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_SORT_KEYS'] = False

app.config['transports'] = 'websocket'
register_routes(app)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

register_routes(app)


@app.route('/alive', methods=['GET'])
def alive():
    return server_response(alive=True)


def notify_web_app_action(event):
    action_type = event['type']
    event_info = event['payload']['info']
    account = event['payload']['account']
    socketio.emit(action_type, event_info, room=account)


@app.route('/alive', methods=['GET'])
def test():
    event = dict(type='search', payload=dict(account='md10fifa@gmail.com', info='search was made'))
    notify_web_app_action(event)
    return server_response(alive=True)


@socketio.on('join')
def on_join(account):
    join_room(account)
    print("JOINED!!")
    socketio.send(f"{account} joined successfully!", room=account)


@socketio.on('leave')
def on_leave(account):
    leave_room(account)
    print("LEFT!!")
    socketio.send(f"{account} has left!", room=account)


socketio.run(app, host=SERVER_IP, debug=True)
