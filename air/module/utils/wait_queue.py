from threading import Timer
from simple_websocket import Client
from sortedcontainers import SortedList
from datetime import datetime
from typing import Optional


class WaitObject:

    def __init__(
        self, 
        speed: int, 
        room_name: str, 
        ws: Client, 
        start_time: datetime
    ) -> None:
        self.speed = speed
        self.room_number = room_number
        self.ws = ws
        self.timer = None
        self.start_time = start_time


class WaitQueue:
    """等待队列实现

    文档中说 "等待队列中需要记录房间号, 风速和分配的等待服务时长"
    我们这样实现
        我们不存储等待服务时长, 而是存储等待结束时间戳, Why?
        想象等待服务时长为计时器, 我们需要实时更新计时器, 这样会增加复杂度,
        此外等待服务时长越小, 说明等待结束时间戳越早, 所以我们直接存储等待结束时间戳

    最终存储的信息为
        (风速, 房间号, WebSocket)
    """

    def __init__(self):
        self.queue = []
        self.wait_dict = {}
        self.time_slist = SortedList()

    def add(self, wait_object: WaitObject):
        self.queue.append(wait_object)
        self.wait_dict[wait_object.room_number] = wait_object
        room_number = wait_object.room_number
        start_time = wait_object.start_time
        self.time_slist.add((start_time, room_number))

    def pop(self, index: int = 0, room_number: Optional[str] = None, oldest: bool = False) -> WaitObject:
        if oldest:
            _, room_number = self.time_slist.pop(0)
            wait_object = self.wait_dict[room_number]
            self.queue.remove(wait_object)
            wait_object.timer.cancel()
            self.wait_dict.pop(wait_object.room_number)
            return wait_object
        
        if room_number is not None:
            wait_object = self.wait_dict[room_number]
            index = self.queue.index(wait_object)
        popped = self.queue.pop(index)
        popped.timer.cancel()
        self.wait_dict.pop(popped.room_number)
        self.time_slist.remove((popped.start_time, popped.room_number))
        return popped

    def empty(self) -> bool:
        return len(self.queue) == 0

    def contains(self, room_number: str) -> bool:
        return room_number in self.wait_dict.keys()

    def get_wind_speed(self, room_number: str) -> int:
        return self.wait_dict[room_number].speed

    def update_wind_speed(self, room_number: str, speed: int):
        self.wait_dict[room_number].speed = speed
