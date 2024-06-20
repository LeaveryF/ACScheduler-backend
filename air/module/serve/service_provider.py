from threading import Thread
from queue import Queue
from datetime import datetime
from json import dumps
from sqlalchemy import desc

from ...db import db, Room, Bill, BillEntry
from ..utils.format_transformer import FormatTransformer


class ServiceProvider(Thread):

    entry_cnt = 0 # 作为BillEntry.entry_id 每次加1 可以改为哈希值
    
    def __init__(self, daemon: bool = True):
        super().__init__(daemon=daemon)
        self.queue = Queue()

    def run(self):
        while True:
            request = self.queue.get()
            
            # 这三个字段是所有请求都有的
            type = request.type
            room_number = request.room_name
            ws = request.ws
            
            # 1. 开关机请求
            if type == "SwitchPower":
                
                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.is_ac_open = request.is_ac_power_on
                db.session.commit()
            
            # 2. 调节请求
            elif type == "Adjust":
                
                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.target_temp = request.target_temp # int 类型
                room.ac_mode = request.target_mode
                room.ac_speed = FormatTransformer.speed(speed=request.target_speed)
                db.session.commit()
            
            # 3. 温度达到请求
            elif type == "TemperatureReached":
                
                # 更新详单BillEntry
                self.update_bill_entry(room_number)
                
                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.current_temp = request.current_temp
                room.ac_speed = 0 # 0表示开机但没送风
                db.session.commit()
            
            # 4. 当前温度请求
            elif type == "CurrentTemperature":
                
                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.current_temp = request.current_temp
                db.session.commit()
            
            # 5. 温度偏移请求
            elif type == "TemperatureDeviated":
                
                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.current_temp = request.current_temp
                db.session.commit()
            
            # 6. 服务器内部构造的DummyPowerOff请求
            elif request.type == "DummyPowerOff":
                
                # 发送停止请求
                message = {
                    "type": "CurrentSpeed",
                    "current_speed": "None"
                }
                ws.send(dumps(message))
                
                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.ac_speed = 0 # 0表示开机但没送风
                
                # 更新详单BillEntry
                self.update_bill_entry(room_number)
                
            # 7. 服务器内部构造的Serve请求
            elif request.type == "Serve":
                
                # 发送风速消息 一定送风
                message = {
                    "type": "CurrentSpeed",
                    "current_speed": request.target_speed
                }
                ws.send(dumps(message))
                
                # 如果上一单未结束 先结算
                self.update_bill_entry(room_number)
                
                # 新增一个详单BillEntry 一定是需要提供新的计费服务的请求
                self.add_bill_entry(room_number, request.target_speed)

                # 更新房间Room
                room = Room.query.filter_by(room_number=room_number).first()
                room.target_temp = request.target_temp # int 类型
                room.ac_mode = request.target_mode
                room.ac_speed = FormatTransformer.speed(speed=request.target_speed)
                db.session.commit()
                
            else:
                raise RuntimeError(f"Invalid request type: {request.type}")
            
    # 新增详单BillEntry
    def add_bill_entry(room_number, target_speed):
        bill = Bill.query.filter_by(room_number=room_number).order_by(desc(Bill.time)).first()
        bill_entry = BillEntry(
            bill_id = bill.bill_id,
            entry_id = entry_cnt, # 可以改为哈希值
            start_time = datetime.now(),
            end_time = datetime.now(), # 不能为空 随便给个值 初始化为当前时间 数据库可以给个默认值
            speed = FormatTransformer.speed(target_speed)
        )
        entry_cnt += 1 # 每次加1 可以改为哈希值
        db.session.add(bill_entry)
        db.session.commit()
    
    # 更新详单BillEntry
    def update_bill_entry(room_number):
        # 按照时间降序 取room_number对应的最晚的账单
        bill = Bill.query.filter_by(room_number=room_number).order_by(desc(Bill.time)).first()
        # 按照时间降序 取bill_id对应的最晚的详单
        bill_entry = BillEntry.query.filter_by(bill_id=bill.bill_id).order_by(desc(BillEntry.time)).first()
        # 如果上一单未结束 才结算
        if bill_entry.start_time == bill_entry.end_time:
            bill_entry.endtime = datetime.now()
            db.session.commit()
        
