from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Room(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(20), nullable=False)
    current_temp = db.Column(db.REAL, nullable=False)
    target_temp = db.Column(db.Integer, nullable=True)
    is_occupied = db.Column(db.Boolean, nullable=False, default=False)
    is_ac_open = db.Column(db.Boolean, nullable=False, default=False)
    ac_mode = db.Column(db.String(20), nullable=True)
    ac_speed = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Room('{self.room_number}', '{self.room_type}', '{self.current_temp}', '{self.target_temp}', '{self.is_occupied}', '{self.is_ac_open}', '{self.ac_mode}', '{self.ac_speed}')"

    def __repr__(self):
        return f"Room('{self.room_number}', '{self.room_type}', '{self.current_temp}', '{self.target_temp}', '{self.is_occupied}', '{self.is_ac_open}', '{self.ac_mode}', '{self.ac_speed}')"


class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"CheckIn('{self.customer_id}', '{self.room_id}')"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"CheckIn('{self.customer_id}', '{self.room_id}')"


class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.String(18), unique=True, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Customer('{self.resident_id}', '{self.name}', '{self.gender}', '{self.contact_number}')"
    contact_number = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Customer('{self.resident_id}', '{self.name}', '{self.gender}', '{self.contact_number}')"


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False)
    check_out_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"History('{self.customer_id}', '{self.room_id}', '{self.check_in_time}', '{self.check_out_time}')"

    def __repr__(self):
        return f"History('{self.customer_id}', '{self.room_id}', '{self.check_in_time}', '{self.check_out_time}')"


class Bill(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    room_cost = db.Column(db.REAL, nullable=False)
    ac_cost = db.Column(db.REAL, nullable=True)

    def __repr__(self):
        return f"Bill('{self.room_id}')"


class BillEntry(db.Model):
    bill_id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    speed = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"BillEntry('{self.bill_id}', '{self.entry_id}', '{self.start_time}', '{self.end_time}', '{self.speed}')"

    def __repr__(self):
        return f"BillEntry('{self.bill_id}', '{self.entry_id}', '{self.start_time}', '{self.end_time}', '{self.speed}')"