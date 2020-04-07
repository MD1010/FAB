import json

from flask import Flask, request, Response
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager
from flask_socketio import SocketIO, join_room, leave_room, send

from active.data import user_login_attempts, active_fabs, opened_drivers
from auth.login import start_login
from auth.login_attempt import LoginAttempt
from auth.selenium_login import set_status_code
from background_threads.thread import open_login_timeout_thread
from consts import server_status_messages
from consts.app import *
from elements.elements_manager import ElementActions
from players.player_search import get_all_players_cards
from players.players_actions import PlayerActions
from user_info.user import initialize_user_from_db
from utils.driver import close_driver
from utils.fab_loop import start_fab
from utils.helper_functions import create_new_fab, append_new_fab_after_auth_success, check_if_web_app_ready, check_if_fab_opened, verify_driver_opened

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['transports'] = 'websocket'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


@app.route('/api/login', methods=['POST'])
def user_login():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    if email in opened_drivers and user_login_attempts[email].is_authenticated:
        return jsonify(msg=server_status_messages.DRIVER_ALREADY_OPENED, code=503)
    if email not in user_login_attempts:
        user_login_attempts[email] = LoginAttempt()
        from background_threads.login_timeout import check_login_timeout
        open_login_timeout_thread(check_login_timeout, email)
    response_obj = start_login(email, password)
    return response_obj


@app.route('/api/start-fab/<string:email>', methods=['POST'])
@check_if_web_app_ready
@check_if_fab_opened
@jwt_required
def start_fab_loop(email):
    jsonData = request.get_json()
    time_to_run = jsonData.get('time')
    requested_players = jsonData.get('requested_players')
    user_driver = opened_drivers[email]
    user_element_actions = ElementActions(user_driver)
    user_player_actions = PlayerActions(user_element_actions)
    fab_user = initialize_user_from_db(email)
    active_fab = create_new_fab(user_driver, user_element_actions, user_player_actions, fab_user)
    append_new_fab_after_auth_success(active_fab, fab_user)
    return start_fab(active_fab, time_to_run, requested_players)


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    result = get_all_players_cards(searched_player)
    return Response(json.dumps(list(map(lambda p: p.player_json(), result))), mimetype="application/json")


@app.route("/api/close-driver/<string:email>")
@verify_driver_opened
def close_running_driver(email):
    driver = opened_drivers[email]
    return close_driver(driver, email)


@app.route("/api/driver-state/<string:email>")
def check_driver_state(email):
    if opened_drivers.get(email):
        return jsonify(state=True)
    else:
        return jsonify(state=False)


@socketio.on('join')
def on_join(data):
    room_id = data["email"]
    join_room(room_id)
    socketio.send("joined successfully!", room=room_id)


@socketio.on('leave')
def on_leave(data):
    user_id = data['userid']
    leave_room(users_rooms.get('user_id'))
    del users_rooms[user_id]


@socketio.on('set_status_code')
def set_code(data):
    code = data['code']
    email = data['email']
    room_id = email
    user_fab = active_fabs.get(email)
    login_attempt = user_login_attempts[email]

    if set_status_code(user_fab, email, code, socketio, room_id):
        send("You successfully loged in", room=room_id)
    elif login_attempt.tries_with_status_code:
        send("Status code error, you have {} attempts left".format(login_attempt.tries_with_status_code), room=room_id)
    else:
        send("You exceeded the max tries to enter the code , restart the app and try again.", room=room_id)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    # cookies = loadCookiesFile("cookies.txt")
    # db.users_collection.update({"_id": ObjectId("5e8916620f5bf4728e39531f")}, {"$set": {"cookies": cookies}})
    socketio.run(app, debug=True)
