import datetime
from typing import Dict, List

from flask import jsonify
from flask_jwt_extended import create_access_token

# username: last_token
access_tokens: Dict[str, List[str]] = {}
refresh_tokens: Dict[str, List[str]] = {}


def refresh_access_token(username):
    new_access_token = create_access_token(identity=username,expires_delta=datetime.timedelta(seconds=5))
    access_tokens[username].append(new_access_token)
    return jsonify(access_token=new_access_token)
