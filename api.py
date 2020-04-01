import json
import threading

import requests
from bson import ObjectId
from flask import Flask, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, send

from auth.login import set_status_code
from auth.signup import sign_up
from consts import server_status_messages
from consts.app import *
from main import Fab
from players.player_search import get_all_players_cards
from utils import db
from utils.driver import close_driver
from utils.helper_functions import loadCookiesFile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#app.config['transports'] = 'websocket'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
fab_driver = Fab()

@app.route('/api/login', methods=['POST'])
def user_login():
    # apend new fab to fab_list
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    response_obj = fab_driver.start_login(email, password)
    return Response(response=response_obj, mimetype="application/json")


@app.route('/api/start-fab', methods=['POST'])
def start_fab_loop():
    jsonData = request.get_json()
    time_to_run = jsonData.get('time')
    requested_players = jsonData.get('requested_players')
    response_obj = fab_driver.start_fab(time_to_run, requested_players)
    return Response(response=response_obj, mimetype="application/json")


@app.route('/api/players-list')
def players_list():
    response = requests.get(url=base_players_url)
    players_json = response.json()
    return Response(response=players_json, mimetype="application/json")


@app.route('/api/players-list/<string:searched_player>', methods=['GET'])
def get_all_cards(searched_player):
    result = get_all_players_cards(searched_player)
    response_obj = json.dumps(list(map(lambda p: p.player_json(), result)))
    return Response(response=response_obj, mimetype="application/json")


@app.route('/api/send-status-code', methods=['POST'])
def send_status_code():
    code = request.get_json()['code']
    response_obj = set_status_code(fab_driver, code)
    return Response(response=response_obj, mimetype="application/json")


@app.route("/api/close-driver")
def close_running_driver():
    response_obj = close_driver(fab_driver)
    return Response(response=response_obj, mimetype="application/json")


@app.route("/api/driver-state")
def check_driver_state():
    return {'state': fab_driver.driver_state.value}


@app.route("/api/signup", methods=['POST'])
def sign_up_user():
    jsonData = request.get_json()
    email = jsonData.get('email')
    password = jsonData.get('password')
    if email is None or password is None:
        return server_status_messages.BAD_REQUEST, 400
    response_obj = sign_up(email, password)
    return Response(response=response_obj, mimetype="application/json")


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
    if set_status_code(fab_driver, code, room_id):
        # room=fab_driver.connected_user_details.get("_id")
        send("You successfully loged in", room=room_id)
    elif fab_driver.tries_with_status_code:
        send("Status code error, you have {} attempts left".format(fab_driver.tries_with_status_code), room=room_id)


if __name__ == '__main__':
    base_players_url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ROOT_URL, BASE_URL, GUID, YEAR, CONTENT_URL, PLAYERS_JSON)
    # cookies = loadCookiesFile("cookies.txt")
    # db.users_collection.update_one({"_id": ObjectId("5e83b84d523912f266eaa77e")}, {"$set": {"cookies": cookies}})
    socketio.run(app)
