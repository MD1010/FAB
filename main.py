import datetime

from flask_jwt_extended import create_access_token
from selenium.common.exceptions import WebDriverException, TimeoutException

from auth.login import check_auth_status, set_auth_status, get_user_details_if_exists, initialize_user_details, check_if_user_has_saved_cookies, login_with_cookies, \
    is_login_successfull_from_first_time, get_status_code_from_user, remember_logged_in_user
from consts import server_status_messages
from elements.elements_manager import initialize_element_actions
from players.players_actions import PlayerActions
from utils.driver import DriverState, check_if_web_app_is_available, close_driver, initialize_time_left, restart_driver_when_crashed, initialize_driver
from utils.fab_loop import run_loop
from utils.helper_functions import jsonify
from utils.server_status import ServerStatus


class Fab:
    def __init__(self):
        self.is_authenticated = False
        self.driver = None
        self.statusCode = ''
        self.element_actions = None
        self.player_actions = None
        self.driver_state = DriverState.OFF
        self.connected_user_details = {}
        self.time_left_to_run = 0

    def start_login(self, email, password):
        user_details = get_user_details_if_exists(email, password)
        if not user_details:
            return jsonify(ServerStatus(server_status_messages.FAILED_AUTH, 401))
        try:
            initialize_user_details(self, user_details)
            initialize_driver(self)
            initialize_element_actions(self)

            if check_if_user_has_saved_cookies(user_details):
                if not login_with_cookies(self, user_details):
                    return jsonify(ServerStatus(server_status_messages.FAILED_AUTH, 401))

            # cookies file was not found - log in the first time
            else:
                if not is_login_successfull_from_first_time(self, email, password):
                    return jsonify(ServerStatus(server_status_messages.FAILED_AUTH, 401))
                status_code_response = get_status_code_from_user(self)
                if not status_code_response:
                    return jsonify(ServerStatus(server_status_messages.LIMIT_TRIES, 401))
                remember_logged_in_user(self)

            success_login_response = ServerStatus(server_status_messages.SUCCESS_AUTH, 200).__dict__
            access_token = create_access_token({'id': str(user_details["_id"])}, expires_delta=datetime.timedelta(hours=1))
            success_login_response["access_token"] = access_token
            return jsonify(success_login_response)

        except TimeoutException:
            print(f"Oops :( Something went wrong..")
            return jsonify(ServerStatus(server_status_messages.FAILED_AUTH, 401))
        except Exception:
            print(f"Server problem.. kill all processes")
            return jsonify(ServerStatus(server_status_messages.DRIVER_ERROR, 503))

    @check_auth_status
    def start_fab(self, time_to_run_in_sec, requested_players):
        if time_to_run_in_sec is None:
            return jsonify(ServerStatus(server_status_messages.BAD_REQUEST, 400))
        try:
            self.player_actions = PlayerActions(self.driver)
            self.element_actions.wait_for_page_to_load()

            if not check_if_web_app_is_available(self):
                run_loop_response = jsonify(ServerStatus(server_status_messages.WEB_APP_NOT_AVAILABLE, 503))
            else:
                self.element_actions.remove_unexpected_popups()
                run_loop_response = run_loop(self, time_to_run_in_sec, requested_players)

            close_driver(self)
            set_auth_status(self, False)
            return run_loop_response

        except (WebDriverException, TimeoutException) as e:
            print(f"Oops :( Something went wrong.. {e.msg}")
            print("restarting FAB...")
            # only if it has not started yet
            if self.time_left_to_run == 0:
                initialize_time_left(self, time_to_run_in_sec)
            restart_driver_when_crashed(self, requested_players)
