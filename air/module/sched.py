import threading
from datetime import datetime
from queue import Queue
from typing import Any, Dict
from simple_websocket import Client

from .serve.service_factory import ServiceFactory
from .serve.service_provider import ServiceProvider
from .utils.wait_queue import WaitQueue
from .utils.serve_queue import ServeQueue
from .utils.wind_speed_mapper import WindSpeedMapper


class Scheduler(threading.Thread):

    def __init__(self, queue: Queue,
                 service_provider: ServiceProvider,
                 capacity: int = 10,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.service_provider = service_provider
        self.serve_queue = ServeQueue(capacity)
        self.wait_queue = WaitQueue()

    def run(self):
        while True:
            if not self.queue.empty():
                room_number, message, ws = self.queue.get()

                message_type = message['type']
                if message_type == 'Adjust':
                    self.handle_adjust(message, ws)
                elif message_type == 'SwitchPower':
                    self.service_provider.serve_switch_power(message, ws)
                elif message_type == 'UpdateCost':
                    self.service_provider.serv_update_cost(message, ws)
                else:
                    self.service_provider.serv_temperature(message, ws)

            if not self.serve_queue.full() and not self.wait_queue.empty():
                # 将等待队列中的对象抽出进行服务
                wait_object = self.wait_queue.pop()
                service_id = self.serve_queue.increase_counter()
                service = ServiceFactory.create_service_by_wait_object(wait_object, service_id)
                self.serve_queue.add(service)
                self.service_provider.serve(service)

            if not self.wait_queue.empty() and \
                    self.wait_queue[0][0] <= datetime.now():
                # 时间片调度策略
                # 将服务队列中的对象踢出
                popped_service = self.serve_queue.pop_oldest()
                wait_object = ServiceFactory.create_wait_object_by_service(popped_service)
                self.wait_queue.add(wait_object)

                # 为等待队列中的对象提供服务
                wait_object = self.wait_queue.pop()
                service_id = self.serve_queue.increase_counter()
                service = ServiceFactory.create_service_by_wait_object(wait_object, service_id)
                self.serve_queue.add(service)
                self.service_provider.serve(service)

    def schedule(self, message: Dict[str, Any], ws: Client):
        target_wind_speed = message['target_speed']
        target_wind_speed = WindSpeedMapper.str_to_int(target_wind_speed)

        # 进行优先级调度
        if self.serve_queue.full():

            # 进入等待队列
            if self.serve_queue[0][0] >= target_wind_speed:
                wait_object = ServiceFactory.create_wait_object(message, ws)
                self.wait_queue.add(wait_object)
                return

            # 优先级更高, 抢占服务对象
            popped_service = self.serve_queue.pop()
            wait_object = ServiceFactory.create_wait_object_by_service(popped_service)
            self.wait_queue.add(wait_object)

        # 进入服务队列
        service_id = self.serve_queue.increase_counter()
        message["service_id"] = service_id
        service = ServiceFactory.create_service(message, ws)
        self.serve_queue.add(service)
        self.service_provider.serve(service)

    def handle_adjust(self, message: Dict[str, Any], ws: Client):
        room_name = message['room_name']
        target_wind_speed = message['target_speed']
        target_wind_speed = WindSpeedMapper.str_to_int(target_wind_speed)
        if self.wait_queue.contains(room_name):
            # 更新等待队列
            self.wait_queue.update_wind_speed(room_name, target_wind_speed)
            return

        if self.serve_queue.contains(room_name):
            old_wind_speed = self.serve_queue.get_room_wind_speed(room_name)
            if old_wind_speed == target_wind_speed:
                # 风速相同, 只是调整温度, 更新目标温度即可
                return

            # 删除旧的服务
            _ = self.serve_queue.pop_by_room_name(room_name)

        self.schedule(message, ws)
