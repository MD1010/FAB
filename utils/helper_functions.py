import bcrypt
from flask import jsonify, make_response
from flask_jwt_extended import get_jwt_identity, create_access_token


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def server_response(code=200, **kwargs):
    res = jsonify(**kwargs)
    return make_response(res, code)


def refresh_access_token():
    current_user = get_jwt_identity()
    return create_access_token(identity=current_user)


def send_pin_event(pin, event_name, **kwargs):
    # events = [self.pin.generate_event('login', status='success')]
    events = [pin.generate_event(event_name, kwargs)]
    pin.send_pin(events)


def destructor(**kwargs):
    return kwargs.values()
