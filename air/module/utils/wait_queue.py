from datetime import datetime
from typing import Tuple
from copy import deepcopy

from simple_websocket import Client
from sortedcontainers import SortedList


class WaitQueue:
    """等待队列实现

    文档中说 "等待队列中需要记录房间号, 风速和分配的等待服务时长"
    我们这样实现
        我们不存储等待服务时长, 而是存储等待结束时间戳, Why?
        想象等待服务时长为计时器, 我们需要实时更新计时器, 这样会增加复杂度,
        此外等待服务时长越小, 说明等待结束时间戳越早, 所以我们直接存储等待结束时间戳

    最终存储的信息为
        (结束等待时间戳, 风速, 房间号, WebSocket)
    """

    def __init__(self):
        self.slist = SortedList()
        self.wait_dict = {}

    def add(self, wait_service: Tuple[datetime, int, str, Client]):
        _, _, room_name, _ = wait_service
        self.slist.add(wait_service)
        self.wait_dict[room_name] = wait_service

    def pop(self, index: int = 0) -> Tuple[datetime, int, str, Client]:
        popped = self.slist.pop(index)
        _, _, room_name, _ = popped
        self.wait_dict.pop(room_name)
        return popped

    def empty(self) -> bool:
        return len(self.slist) == 0

    def contains(self, room_name: str) -> bool:
        return room_name in self.wait_dict.keys()

    def update_wind_speed(self, room_name: str, wind_speed: int):
        old = deepcopy(self.wait_dict[room_name])
        old[1] = wind_speed
        self.update(old)

    def update(self, wait_service: Tuple[datetime, int, str, Client]):
        _, _, room_name, _ = wait_service
        old = self.wait_dict[room_name]
        self.slist.remove(old)
        self.slist.add(wait_service)
        self.wait_dict[room_name] = wait_service

    def __getitem__(self, index: int) -> Tuple[datetime, int, str, Client]:
        return self.slist[index]
