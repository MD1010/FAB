from flask import Blueprint
from flask_jwt_extended import jwt_refresh_token_required

from utils.helper_functions import refresh_access_token

auth = Blueprint("auth", __name__)

@auth.route('/get-new-access-token', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    return refresh_access_token()

