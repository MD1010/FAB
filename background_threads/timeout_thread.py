import threading


def open_login_timeout_thread(func, email,app):
    new_thread = threading.Thread(target=func, args=(email,app))
    new_thread.start()

