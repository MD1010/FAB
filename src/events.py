import src


class ServerEvents:
    def __init__(self):
        """
            emitted events from server
        """

    def emit_waiting_status_code_event(self):
        src.messages.append('waiting for status code')
        print(1)
