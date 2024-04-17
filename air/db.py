from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Room(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(20), nullable=False)
    current_temp = db.Column(db.REAL, nullable=False)
    target_temp = db.Column(db.Integer, nullable=True)
    is_occupied = db.Column(db.Boolean, nullable=False, default=False)
    is_ac_open = db.Column(db.Boolean, nullable=False, default=False)
    ac_mode = db.Column(db.String(20), nullable=True)
    ac_speed = db.Column(db.Integer, nullable=True)
    ac_cost = db.Column(db.REAL, nullable=True)


class CheckIn(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, primary_key=True)


class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.String(18), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime, nullable=False)


class Bill(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, nullable=False)


class BillEntry(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
