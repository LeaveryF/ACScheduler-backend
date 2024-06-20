import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash
from .db import db, User, Room, CheckIn, Bill, BillEntry, Customer, History


def datetime_from_string(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def load_jsonl(file_path):
    with open(file_path, "r") as f:
        return [json.loads(line) for line in f]


def seed_data():
    users = [
        {"username": "manager", "password": "manager"},
        {"username": "acadmin", "password": "acadmin"},
        {"username": "receptionist", "password": "receptionist"},
    ]

    rooms = load_jsonl(os.path.join(os.path.dirname(__file__), "tmp", "room.jsonl"))
    bills = load_jsonl(os.path.join(os.path.dirname(__file__), "tmp", "bill.jsonl"))
    billentries = load_jsonl(os.path.join(os.path.dirname(__file__), "tmp", "billentry.jsonl"))
    customers = load_jsonl(os.path.join(os.path.dirname(__file__), "tmp", "customer.jsonl"))
    histories = load_jsonl(os.path.join(os.path.dirname(__file__), "tmp", "history.jsonl"))


    # checkins = [
    #     {"customer_id": 1, "room_id": 1, "time": "2021-01-01 00:00:00"},
    #     {"customer_id": 2, "room_id": 2, "time": "2021-01-01 00:00:00"},
    #     {"customer_id": 3, "room_id": 3, "time": "2021-01-01 00:00:00"},
    # ]

    for user in users:
        user = User(
            username=user["username"], password=generate_password_hash(user["password"])
        )
        db.session.add(user)

    for room in rooms:
        room = Room(
            room_id=room["room_id"],
            room_number=room["room_number"],
            room_type=room["room_type"],
            current_temp=room["current_temp"],
        )
        db.session.add(room)

    for customer in customers:
        customer = Customer(
            customer_id=customer["customer_id"],
            resident_id=customer["resident_id"],
            name=customer["name"],
            gender=customer["gender"],
            contact_number=customer["contact_number"],
        )
        db.session.add(customer)

    # for checkin in checkins:
    #     checkin = CheckIn(
    #         customer_id=checkin["customer_id"],
    #         room_id=checkin["room_id"],
    #         time=datetime_from_string(checkin["time"]),
    #     )
    #     db.session.add(checkin)

    for bill in bills:
        bill = Bill(
            room_id=bill["room_id"],
            time=datetime_from_string(bill["time"]),
            room_cost=bill["room_cost"],
            ac_cost=bill["ac_cost"],
        )
        db.session.add(bill)

    for billentry in billentries:
        billentry = BillEntry(
            bill_id=billentry["bill_id"],
            entry_id=billentry["entry_id"],
            start_time=datetime_from_string(billentry["start_time"]),
            end_time=datetime_from_string(billentry["end_time"]),
            speed=billentry["speed"],
        )
        db.session.add(billentry)

    for history in histories:
        history = History(
            customer_id=history["customer_id"],
            room_id=history["room_id"],
            check_in_time=datetime_from_string(history["check_in_time"]),
            check_out_time=datetime_from_string(history["check_out_time"]),
        )
        db.session.add(history)

    db.session.commit()
