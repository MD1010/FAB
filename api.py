import json

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager
from flask_socketio import SocketIO, join_room, leave_room, send

from auth.login import start_login
from auth.login_attempt import LoginAttempt
from auth.selenium_login import set_status_code
from consts import server_status_messages
from consts.app import *
from consts.server_status_messages import LIMIT_TRIES
from live_data import user_login_attempts, active_fabs, opened_drivers
from players.player_cards import get_all_players_cards
from players.players_actions import ItemActions
from user_info.user_actions import initialize_user_from_db
from utils.driver_functions import close_driver
from utils.elements_manager import ElementActions
from utils.helper_functions import create_new_fab, append_new_fab_after_auth_success, verify_driver_opened, server_response, check_if_web_app_ready, check_if_fab_opened
from utils.login_timeout_thread import check_login_timeout, open_login_timeout_thread
from utils.start_fab import start_fab

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
        return server_response(msg=server_status_messages.DRIVER_ALREADY_OPENED, code=503)
    if email not in user_login_attempts:
        user_login_attempts[email] = LoginAttempt()
        open_login_timeout_thread(check_login_timeout, email, app)
    response_obj = start_login(email, password)
    return response_obj


@app.route('/api/start-fab', methods=['POST'])
@check_if_web_app_ready
@check_if_fab_opened
@jwt_required
def start_fab_loop():
    jsonData = request.get_json()
    configuration_data = jsonData.get('loopConfiguration')
    user_email = jsonData.get('user')
    user_items_with_prices = jsonData.get('userPlayerPrices')
    requested_items = jsonData.get('itemsToSearch')
    user_driver = opened_drivers[user_email]
    user_element_actions = ElementActions(user_driver)
    user_item_actions = ItemActions(user_element_actions)
    fab_user = initialize_user_from_db(user_email)
    active_fab = create_new_fab(user_driver, user_element_actions, user_item_actions, fab_user)
    append_new_fab_after_auth_success(active_fab, fab_user)
    return start_fab(active_fab, configuration_data, requested_items, user_items_with_prices)


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    result = get_all_players_cards(searched_player)
    return Response(json.dumps(list(map(lambda p: p.player_json(), result))), mimetype="application/json")


@app.route("/api/close-driver", methods=['GET'])
@verify_driver_opened
def close_running_driver():
    jsonData = request.get_json()
    email = jsonData.get('user')
    driver = opened_drivers[email]
    return close_driver(driver, email)


@app.route("/api/driver-state")
def check_driver_state():
    jsonData = request.get_json()
    email = jsonData.get('user')
    if opened_drivers.get(email):
        return jsonify(active=True)
    else:
        return jsonify(active=False)


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
        send(LIMIT_TRIES, room=room_id)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    socketio.run(app, debug=True)
