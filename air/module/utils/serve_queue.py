from datetime import datetime
from typing import Tuple
from simple_websocket import Client
from sortedcontainers import SortedList


class ServeQueue:
    """服务队列实现

    文档中说 "服务队列中需要记录房间号和服务对象的ID, 风速以及服务时长"
    我们这样实现
        1. 服务队列中存储服务对象, 可按数组索引获取服务对象
        2. 服务对象的 ID 依次定增
        3. 只存储服务开始的时间戳, 不单独存储服务时长

    最终存储的信息为
        (风速, 服务开始时间戳, 服务对象ID, 房间号, WebSocket)

    注意:
        1. SortedList 默认按升序排序, 风速越小越靠前
        2. 当风速相同时, 按服务开始时间戳升序排序, 即越早开始的服务越靠前
        3. 如果风速和服务开始时间戳都相同, 则按服务对象ID升序排序, 即越早加入队列的服务越靠前 (一般不会出现服务开始时间戳一样的情况)
        4. 房间号不参与排序, 因为服务对象ID已经唯一标识了服务对象
        5. WebSocket 用来通信, 不参与排序
    """

    def __init__(self, capacity: int):
        self.slist = SortedList()
        self.time_list = SortedList()
        self.counter = 0
        self.capacity = capacity
        self.serv_dict = {}

    def full(self) -> bool:
        return len(self.slist) >= self.capacity

    def increase_counter(self) -> int:
        tmp = self.counter
        self.counter += 1
        return tmp

    def add(self, service: Tuple[int, datetime, int, str, Client]):
        _, begin, _, room_name, _ = service
        self.slist.add(service)
        self.serv_dict[room_name] = service
        self.time_list.add((begin, room_name))

    def contains(self, room_name: str) -> bool:
        return room_name in self.serv_dict.keys()

    def get_room_wind_speed(self, room_name: str) -> int:
        wind_speed, _, _, _, _ = self.serv_dict[room_name]
        return wind_speed

    def update(self, service: Tuple[int, datetime, int, str, Client]):
        _, _, _, room_name, _ = service
        old = self.serv_dict[room_name]
        self.serv_dict.pop(room_name)
        self.slist.remove(old)
        self.slist.add(service)
        # time_list 不需要改变

    def pop_by_room_name(self, room_name: str) -> Tuple[int, datetime, int, str, Client]:
        old = self.serv_dict[room_name]
        _, begin, _, _, _ = old
        self.serv_dict.pop(room_name)
        self.slist.remove(old)
        self.time_list.remove((begin, room_name))
        return old

    def pop_oldest(self) -> Tuple[int, datetime, int, str, Client]:
        _, room_name = self.time_list.pop(-1)
        oldest = self.serv_dict[room_name]
        self.serv_dict.pop(room_name)
        self.slist.remove(oldest)
        return oldest

    def pop(self, index: int = 0) -> Tuple[int, datetime, int, str, Client]:
        popped = self.slist.pop(index)
        _, begin, _, room_name, _ = popped
        self.serv_dict.pop(room_name)
        self.time_list.remove((begin, room_name))
        return popped

    def __getitem__(self, index: int) -> Tuple[int, datetime, int, str, Client]:
        return self.slist[index]
