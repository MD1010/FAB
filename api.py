from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity, jwt_refresh_token_required
from flask_socketio import SocketIO, join_room, leave_room, send

from auth.app_users.login import log_in_user
from auth.app_users.signup import create_new_user
from auth.web_app.login import start_ea_account_login
from auth.web_app.login_attempt import LoginAttempt
from auth.web_app.selenium_login import set_status_code
from consts import server_status_messages
from consts.app import *
from consts.server_status_messages import LIMIT_TRIES
from ea_account_info.ea_account_actions import initialize_ea_account_from_db
from fab_loop.start_fab import start_fab
from items.item_actions import ItemActions
from live_data import ea_account_login_attempts, opened_drivers
from players.player_cards import get_all_players_cards
from users.subscription_plan import update_user_subscription_plan, check_if_valid_subscription
from users.user_details import update_user_username, update_user_password
from users.user_ea_accounts import add_ea_account_to_user, delete_ea_account_from_user, check_if_user_owns_ea_account
from utils.driver_functions import close_driver
from utils.elements_manager import ElementActions
from utils.helper_functions import create_new_fab, append_new_fab_after_auth_success, verify_driver_opened, server_response, check_if_web_app_ready, check_if_fab_opened, \
    refresh_access_token
from utils.login_timeout_thread import check_login_timeout, open_login_timeout_thread

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
jwt = JWTManager(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['transports'] = 'websocket'
app.config['JSON_SORT_KEYS'] = False
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


@app.route('/get-new-access-token', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    return refresh_access_token()


@app.route('/api/signup', methods=['POST'])
def sign_up_user():
    json_data = request.get_json()
    username = json_data.get('username')
    password = json_data.get('password')
    return create_new_user(username, password)


@app.route('/api/login', methods=['POST'])
def login():
    json_data = request.get_json()
    username = json_data.get('username')
    password = json_data.get('password')
    return log_in_user(username, password)


@app.route('/api/edit-username', methods=['POST'])
@jwt_required
def edit_username():
    json_data = request.get_json()
    # make sure to log again to fetch an updated useraname
    old_username = get_jwt_identity()['username']
    new_username = json_data.get('new_username')
    return update_user_username(old_username, new_username)


@app.route('/api/edit-password', methods=['POST'])
@jwt_required
def edit_password():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    new_password = json_data.get('new_password')
    return update_user_password(username, new_password)


@app.route('/api/add-ea-account', methods=['POST'])
@jwt_required
def add_user_ea_account():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    ea_account = json_data.get('ea_account')
    return add_ea_account_to_user(username, ea_account)


@app.route('/api/delete-ea-account', methods=['POST'])
@jwt_required
def delete_user_ea_account():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    ea_account = json_data.get('ea_account')
    return delete_ea_account_from_user(username, ea_account)


@app.route('/api/update-user-plan', methods=['POST'])
@jwt_required
def update_user_plan():
    json_data = request.get_json()
    username = get_jwt_identity()['username']
    new_plan_type = json_data.get('new_plan_type')
    return update_user_subscription_plan(username, new_plan_type)


@app.route('/api/ea-account-login', methods=['POST'])
@jwt_required
@check_if_valid_subscription
@check_if_user_owns_ea_account
def ea_account_login():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    owner = get_jwt_identity()['username']
    if email in opened_drivers and ea_account_login_attempts[email].is_authenticated:
        return server_response(msg=server_status_messages.DRIVER_ALREADY_OPENED, code=503)
    if email not in ea_account_login_attempts:
        ea_account_login_attempts[email] = LoginAttempt()
        open_login_timeout_thread(check_login_timeout, email, app)
    response_obj = start_ea_account_login(owner, email, password)
    return response_obj


@app.route('/api/start-fab', methods=['POST'])
@jwt_required
@check_if_valid_subscription
@check_if_fab_opened
@check_if_web_app_ready
def start_fab_loop():
    json_data = request.get_json()
    configuration = json_data.get('configuration')
    items = json_data.get('items')
    owner = get_jwt_identity()['username']
    ea_account = json_data.get('ea_account')
    user_driver = opened_drivers[ea_account]
    user_element_actions = ElementActions(user_driver)
    user_item_actions = ItemActions(user_element_actions)
    fab_user = initialize_ea_account_from_db(owner, ea_account)
    active_fab = create_new_fab(user_driver, user_element_actions, user_item_actions, fab_user)
    append_new_fab_after_auth_success(active_fab, fab_user)
    return start_fab(active_fab, configuration, items)


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
@jwt_required
def get_all_cards(searched_player):
    return jsonify(get_all_players_cards(searched_player))


@app.route("/api/close-driver", methods=['GET'])
@verify_driver_opened
@jwt_required
def close_running_driver():
    jsonData = request.get_json()
    ea_account = jsonData.get('ea_account')
    driver = opened_drivers[ea_account]
    return close_driver(driver, ea_account)


@app.route("/api/driver-state")
def check_driver_state():
    jsonData = request.get_json()
    email = jsonData.get('ea_account')
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
    leave_room(user_rooms.get('user_id'))
    del user_rooms[user_id]


@socketio.on('set_status_code')
def set_code(data):
    code = data['code']
    email = data['email']
    room_id = email
    driver = opened_drivers.get(email)
    login_attempt = ea_account_login_attempts[email]

    if set_status_code(driver, email, code, socketio, room_id):
        send("You successfully loged in", room=room_id)
    elif login_attempt.tries_with_status_code:
        send("Status code error, you have {} attempts left".format(login_attempt.tries_with_status_code), room=room_id)
    else:
        send(LIMIT_TRIES, room=room_id)
        close_driver(driver, email)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    socketio.run(app, debug=True)
