from .db import db, User, Room
from werkzeug.security import generate_password_hash


def seed_data():
    users = [
        {
            'username': 'manager',
            'password': 'manager'
        },
        {
            'username': 'acadmin',
            'password': 'acadmin'
        },
        {
            'username': 'receptionist',
            'password': 'receptionist'
        }
    ]

    rooms = [
        {
            'room_name': '1101',
            'room_type': '六人间',
            'current_temp': '25',
        },
        {
            'room_name': '1102',
            'room_type': '六人间',
            'current_temp': '25'
        },
        {
            'room_name': '1103',
            'room_type': '六人间',
            'current_temp': '25'
        },
    ]

    for user in users:
        user = User(
            username=user['username'],
            password=generate_password_hash(user['password'])
        )
        db.session.add(user)

    for room in rooms:
        room = Room(
            room_name=room['room_name'],
            room_type=room['room_type'],
            current_temp=room['current_temp']
        )
        db.session.add(room)

    db.session.commit()
