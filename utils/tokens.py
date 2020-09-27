from typing import Dict

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, create_access_token

# username: last_token
access_tokens: Dict[str, str] = {}
refresh_tokens: Dict[str, str] = {}


def refresh_access_token():
    current_user = get_jwt_identity()['username']
    new_access_token = create_access_token(identity=current_user)
    access_tokens[current_user] = new_access_token
    return jsonify(access_token=new_access_token)
