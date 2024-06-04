import os
import json
import random
from string import ascii_letters
from datetime import datetime, timedelta

os.makedirs("tmp", exist_ok=True)

"""

生成房间

"""

room_types = ["单人间", "双人间", "三人间", "四人间", "五人间", "六人间"]
rooms = []

for i in range(1, 101):
    room = {
        "room_id": i,
        "room_number": str(i),
        "room_type": random.choice(room_types),
        "current_temp": random.randint(18, 30),
    }
    rooms.append(room)

with open("tmp/room.jsonl", "w") as f:
    for room in rooms:
        f.write(json.dumps(room) + "\n")


"""

生成顾客

"""

customers = []

unique_ids = [13 * i + 10077 for i in range(10000)]

for i in range(1, 1001):
    customer = {
        "customer_id": i,
        "resident_id": unique_ids[i],
        "name": "".join(random.choices(ascii_letters, k=10)),
        "gender": random.choice(["男", "女", "未知"]),
        "contact_number": "1" + "".join(random.choices("0123456789", k=10)),
    }
    customers.append(customer)

with open("tmp/customer.jsonl", "w") as f:
    for customer in customers:
        f.write(json.dumps(customer) + "\n")

"""

生成入住历史

"""

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
histories = []
bills = []
billentries = []

# 从2024年1月1日开始生成入住历史, 每隔两天生成一条入住记录, 持续到10天前
date = datetime(2024, 1, 1)
while date < datetime.now() - timedelta(days=10):
    check_in_time = date
    check_out_time = date + timedelta(days=1)
    checkin_customer = random.choice(customers)
    checkin_room = random.choice(rooms)

    history = {
        "customer_id": checkin_customer["customer_id"],
        "room_id": checkin_room["room_id"],
        "check_in_time": check_in_time.strftime("%Y-%m-%d %H:%M:%S"),
        "check_out_time": check_out_time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    histories.append(history)
    
    start = check_in_time
    ac_cost = 0
    for i in range(8): # 8小时, 一小时一条记录
        billentry = {
            "bill_id": len(bills) + 1,
            "entry_id": len(billentries) + 1,
            "start_time": start.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (start + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "speed": random.randint(1, 3),
        }
        billentries.append(billentry)
        ac_cost += speed_cost_dict[billentry["speed"]] * 3600
        start += timedelta(hours=1)

    bill = {
        "room_id": checkin_room["room_id"],
        "time": check_in_time.strftime("%Y-%m-%d %H:%M:%S"),
        "room_cost": room_cost_dict[checkin_room["room_type"]],
        "ac_cost": ac_cost
    }
    
    bills.append(bill)
    date += timedelta(days=2)

with open("tmp/history.jsonl", "w") as f:
    for history in histories:
        f.write(json.dumps(history) + "\n")
        
with open("tmp/bill.jsonl", "w") as f:
    for bill in bills:
        f.write(json.dumps(bill) + "\n")

with open("tmp/billentry.jsonl", "w") as f:
    for billentry in billentries:
        f.write(json.dumps(billentry) + "\n")