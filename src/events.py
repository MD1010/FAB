from flask_socketio import join_room, leave_room


def initSocketEvents(socketio):
    @socketio.on('join')
    def on_join(data):
        room_id = data['username']
        join_room(room_id)
        socketio.send(f"{room_id} joined successfully!", room=room_id)

#
# @socketio.on('leave')
# def on_leave(data):
#     user_id = data['userid']
#     leave_room(user_rooms.get('user_id'))
