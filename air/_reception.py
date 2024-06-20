from flask import Blueprint, render_template, request, redirect, url_for
from .auth import reception_required
from .db import db, Room, CheckIn, Customer, History, Bill, BillEntry
from datetime import datetime


bp = Blueprint("reception", __name__, url_prefix="/reception")

room_cost_dict = {
    "单人间": 100,
    "双人间": 200,
    "三人间": 300,
    "四人间": 400,
    "五人间": 500,
    "六人间": 600,
}

speed_cost_dict = {
    0: 0,
    1: 1 / (3 * 60),  # 低风 1￥/3min
    2: 1 / (2 * 60),  # 中风 1￥/2min
    3: 1 / 60,  # 高风 1￥/1min
}


@bp.route("/home")
@reception_required
def home():
    return render_template("reception/home.html")


@bp.route("/checkin", methods=("GET", "POST"))
@reception_required
def checkin():
    if request.method == "POST":
        guest_name = request.form["guest-name"]
        guest_gender = request.form["guest-gender"]
        guest_id = request.form["guest-id"]
        contact_number = request.form["contact-number"]
        room_number = request.form["room-number"]
        checkin_date = request.form["checkin-date"]
        checkout_date = request.form["checkout-date"]

        checkin_date = datetime.fromisoformat(checkin_date)
        checkout_date = datetime.fromisoformat(checkout_date)

        customer = Customer.query.filter_by(resident_id=guest_id).first()
        if not customer:  # 如果客户不存在, 则添加客户
            customer = Customer(
                resident_id=guest_id,
                name=guest_name,
                gender=guest_gender,
                contact_number=contact_number,
            )
            db.session.add(customer)

        room = Room.query.filter_by(room_number=room_number).first()
        room.is_occupied = True

        checkin = CheckIn(
            customer_id=customer.customer_id,
            room_id=room.room_id,
            time=checkin_date,
        )
        db.session.add(checkin)

        history = History(
            customer_id=customer.customer_id,
            room_id=room.room_id,
            check_in_time=checkin_date,
            check_out_time=checkout_date,
        )
        db.session.add(history)

        bill = Bill(
            room_id=room.room_id,
            time=checkin_date,
            room_cost=room_cost_dict[room.room_type],
        )
        db.session.add(bill)

        db.session.commit()
        return redirect(url_for("reception.checkin", checkinOk=True))

    checkinOk = request.args.get("checkinOk", False)
    rooms = Room.query.filter_by(is_occupied=False).all()
    return render_template("reception/checkin.html", rooms=rooms, checkinOk=checkinOk)


@bp.route("/checkout", methods=("GET", "POST"))
@reception_required
def checkout():
    if request.method == "POST":
        _ = request.form["guest-name"]
        id_number = request.form["id-number"]
        customer = Customer.query.filter_by(resident_id=id_number).first()
        if not customer:
            return render_template(
                "reception/checkout.html", showpopup=True, popupmsg="客户不存在"
            )

        checkin = CheckIn.query.filter_by(customer_id=customer.customer_id).first()
        if not checkin:
            return render_template(
                "reception/checkout.html", showpopup=True, popupmsg="客户未入住"
            )
        room = Room.query.filter_by(room_id=checkin.room_id).first()
        if not room:
            return render_template(
                "reception/checkout.html", showpopup=True, popupmsg="房间不存在"
            )

        room.is_occupied = False
        bill = Bill.query.filter_by(room_id=room.room_id, time=checkin.time).first()
        bill_entries = BillEntry.query.filter_by(bill_id=bill.bill_id).all()
        ac_cost = 0
        for bill_entry in bill_entries:
            ac_cost += (
                bill_entry.end_time - bill_entry.start_time
            ).seconds * speed_cost_dict[bill_entry.speed]
        bill.ac_cost = ac_cost
        db.session.delete(checkin)
        db.session.commit()

        return render_template(
            "reception/checkout.html",
            showpopup=True,
            room_cost=bill.room_cost,
            ac_cost=ac_cost,
            total_cost=bill.room_cost + ac_cost,
            bill_entries=bill_entries,
        )

    return render_template("reception/checkout.html", showpopup=False)
