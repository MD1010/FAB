import bcrypt
from flask import jsonify, make_response
from cryptography.fernet import Fernet


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def encrypt_password(password):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_password = f.encrypt(bytes(password, encoding='utf8'))
    return encrypted_password, key

def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    password = f.decrypt(encrypted_password)
    return password.decode("utf-8")

def server_response(code=200, **kwargs):
    res = jsonify(**kwargs)
    return make_response(res, code)


def destructor(**kwargs):
    return kwargs.values()
