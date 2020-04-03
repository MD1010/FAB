import json

from flask import Flask, request, Response
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager
from flask_socketio import SocketIO, join_room, leave_room, send

from active.data import users_attempted_login
from auth.login import  start_login
from auth.login_attempt import LoginAttempt
from auth.signup import register_new_user_to_db
from background_threads.login_timeout import check_login_timeout
from background_threads.thread import open_thread
from consts import server_status_messages
from consts.app import *
from fab import Fab
from players.player_search import get_all_players_cards
from utils.driver import close_driver
from utils.fab_loop import start_fab

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['transports'] = 'websocket'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


@app.route('/api/login', methods=['POST'])
def user_login():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    if email not in users_attempted_login:
        login_session = LoginAttempt()
        users_attempted_login[email] = login_session
        users_attempted_login.get(email).login_thread = open_thread(check_login_timeout, email)
    response_obj = start_login(email, password)

    return response_obj


@app.route('/api/start-fab/<int:id>', methods=['POST'])
@jwt_required
def start_fab_loop():
    jsonData = request.get_json()
    time_to_run = jsonData.get('time')
    requested_players = jsonData.get('requested_players')
    return start_fab(time_to_run, requested_players)


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
@jwt_required
def get_all_cards(searched_player):
    result = get_all_players_cards(searched_player)
    return Response(json.dumps(list(map(lambda p: p.player_json(), result))), mimetype="application/json")


@app.route("/api/close-driver")
# @jwt_required
def close_running_driver():
    return close_driver(fab_driver)


@app.route("/api/driver-state")
@jwt_required
def check_driver_state():
    return jsonify(state=fab_driver.driver_state.value)


@app.route("/api/signup", methods=['POST'])
def sign_up_user():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    if email is None or password is None:
        return server_status_messages.BAD_REQUEST, 400
    return register_new_user_to_db(email, password)


@socketio.on('join')
def on_join():
    user_id = fab_driver.connected_user_details.get("_id")
    join_room(user_id)
    # users_rooms[user_id] = user_id
    # emit('joined', "You successfully enter the room", room=user_id)
    send("joined successfully!", room=user_id)


@socketio.on('leave')
def on_leave(data):
    user_id = data['userid']
    leave_room(users_rooms.get('user_id'))
    del users_rooms[user_id]


@socketio.on('set_status_code')
def set_code(data):
    code = data['code']
    room_id = fab_driver.connected_user_details.get("_id")

    # send("Status code error, you have {} attempts left".format(fab_driver.tries_with_status_code), room=1)
    # todo get the email of the user
    if set_status_code(fab_driver, code, socketio, room_id):
        # room=fab_driver.connected_user_details.get("_id")
        send("You successfully loged in", room=room_id)
    elif fab_driver.tries_with_status_code:
        send("Status code error, you have {} attempts left".format(fab_driver.tries_with_status_code), room=room_id)
    else:
        send("You exceeded the max tries to enter the code , restart the app and try again.", room=room_id)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    # cookies = loadCookiesFile("cookies.txt")
    # db.users_collection.update_one({"_id": ObjectId("5e850e639cfb2c84a70de8fa")}, {"$set": {"cookies": cookies}})
    socketio.run(app, debug=True)
