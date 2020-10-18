import bcrypt
import os
from flask import jsonify, make_response
from cryptography.fernet import Fernet


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def encrypt_password(password):
    key = bytes(os.getenv("PASSWORD_KEY"), encoding='utf8')
    f = Fernet(key)
    encrypted_password = f.encrypt(bytes(password, encoding='utf8'))
    return encrypted_password

def decrypt_password(encrypted_password):
    key = bytes(os.getenv("PASSWORD_KEY"), encoding='utf8')
    f = Fernet(key)
    password = f.decrypt(encrypted_password)
    return password.decode("utf-8")

def server_response(code=200, **kwargs):
    res = jsonify(**kwargs)
    return make_response(res, code)


def destructor(**kwargs):
    return kwargs.values()
