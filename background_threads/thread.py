import threading


def open_thread(func, email):
    new_thread = threading.Thread(target=func, args=(email,))
    new_thread.start()

