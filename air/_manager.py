from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from .auth import manager_required
from .db import db, Room, History, Customer, Bill, BillEntry
import plotly.express as px
import plotly.utils
import pandas as pd
import json
from ._reception import speed_cost_dict


bp = Blueprint("manager", __name__, url_prefix="/manager")


def income_chart():
    bills = (
        db.session.query(
            Bill.time,
            Bill.room_cost,
            Bill.ac_cost,
        )
        .filter(Bill.ac_cost.isnot(None))
        .all()
    )

    df = pd.DataFrame(
        [
            {
                "time": bill.time,
                "room_cost": bill.room_cost,
                "ac_cost": bill.ac_cost,
            }
            for bill in bills
        ]
    )

    if df.empty:
        return None

    df['time'] = pd.to_datetime(df['time'])
    df['date'] = df['time'].dt.date
    df = df.groupby('date')[['room_cost', 'ac_cost']].sum().reset_index()
    df['total_income'] = df['room_cost'] + df['ac_cost']

    fig = px.line(
        df,
        x="date",
        y="total_income",
        title="酒店收入统计",
        labels={"date": "日期", "total_income": "收入"},
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def income_pie_chart():
    bills = (
        db.session.query(
            Bill.room_cost,
            Bill.ac_cost,
        )
        .filter(Bill.ac_cost.isnot(None))
        .all()
    )

    df = pd.DataFrame(
        [
            {
                "房间收入": bill.room_cost,
                "空调收入": bill.ac_cost,
            }
            for bill in bills
        ]
    )

    if df.empty:
        return None

    df = df.sum().reset_index()
    df.columns = ['cost_type', 'total_cost']

    fig = px.pie(
        df,
        values="total_cost",
        names="cost_type",
        title="收入来源统计",
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


@bp.route("/report")
@manager_required
def report():
    now = datetime.now()
    checkin_histories = (
        db.session.query(
            History.id,
            (Customer.name).label("customer_name"),
            Room.room_number,
            History.check_in_time,
            (History.check_out_time <= now).label("is_checked_out"),
        )
        .filter(
            History.room_id == Room.room_id, History.customer_id == Customer.customer_id
        )
        .order_by(History.id.desc())
        .all()
    )

    request_id = request.args.get("id", None)
    if request_id:
        history = History.query.filter_by(id=request_id).first()
        bill = Bill.query.filter_by(room_id=history.room_id, time=history.check_in_time).first()
        bill_entries = BillEntry.query.filter_by(bill_id=bill.bill_id).all()

        if bill.ac_cost:
            ac_cost = bill.ac_cost
        else:
            ac_cost = 0
            for bill_entry in bill_entries:
                if bill_entry.end_time:
                    ac_cost += (bill_entry.end_time - bill_entry.start_time).seconds * speed_cost_dict[bill_entry.speed]
                else:
                    ac_cost += (datetime.now() - bill_entry.start_time).seconds * speed_cost_dict[bill_entry.speed]
        
        
        return render_template(
            "manager/report.html",
            checkin_histories=checkin_histories,
            income_chart_json=income_chart(),
            income_pie_chart_json=income_pie_chart(),
            showpopup=True,
            room_cost=bill.room_cost,
            ac_cost=ac_cost,
            total_cost=bill.room_cost + ac_cost,
            bill_entries=bill_entries,
        )


    return render_template(
        "manager/report.html",
        checkin_histories=checkin_histories,
        income_chart_json=income_chart(),
        income_pie_chart_json=income_pie_chart(),
    )
