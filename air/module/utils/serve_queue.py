from datetime import datetime
from typing import Dict, Optional
from simple_websocket import Client
from sortedcontainers import SortedList


class ServeObject:
    """ServeObject 必须可以比较, 并且比较起来像 Tuple
    (风速, 服务开始时间戳, 服务对象ID, 房间号, WebSocket)
    """

    def __init__(
        self,
        speed: int,
        start_time: datetime,
        service_id: int,
        room_number: str,
        ws: Client,
        temp: int,
        mode: str
    ) -> None:
        self.speed = speed
        self.start_time = start_time
        self.service_id = service_id
        self.room_number = room_number
        self.ws = ws
        self.temp = temp
        self.mode = mode


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
        self.serv_dict: Dict[str, ServeObject] = {}
        self.speed_slist = SortedList()
        self.time_slist = SortedList()
        self.capacity = capacity

    def full(self) -> bool:
        return len(self.speed_slist) >= self.capacity

    def add(self, serve_object: ServeObject):
        speed = serve_object.speed
        start_time = serve_object.start_time
        room_number = serve_object.room_number
        self.serv_dict[room_number] = serve_object
        self.speed_slist.add((speed, start_time, room_number))
        self.time_slist.add((start_time, serve_object.room_number))

    def contains(self, room_number: str) -> bool:
        return room_number in self.serv_dict.keys()

    def get_wind_speed(self, room_number: str) -> int:
        return self.serv_dict[room_number].speed

    def update(self, serve_object: ServeObject):
        speed = serve_object.speed
        start_time = serve_object.start_time
        room_number = serve_object.room_number
        old = self.serv_dict[room_number]
        self.serv_dict[room_number] = serve_object
        self.speed_slist.remove((old.speed, old.start_time, room_number))
        self.speed_slist.add((speed, start_time, room_number))
        # time_slist 不需要改变

    def pop(self, oldest=False, room_number: Optional[str] = None) -> ServeObject:
        if room_number is not None:
            serve_object = self.serv_dict[room_number]
            self.serv_dict.pop(room_number)
            self.speed_slist.remove((serve_object.speed, serve_object.start_time, room_number))
            self.time_slist.remove((serve_object.start_time, room_number))
            return serve_object
        
        if oldest:
            _, room_number = self.time_slist.pop(0)
            serve_object = self.serv_dict[room_number]
            self.serv_dict.pop(room_number)
            self.speed_slist.remove((serve_object.speed, serve_object.start_time, room_number))
            return serve_object
        else:
            _, start_time, room_number = self.speed_slist.pop(0)
            serve_object = self.serv_dict[room_number]
            self.serv_dict.pop(room_number)
            self.time_slist.remove((start_time, room_number))
            return serve_object

    def __getitem__(self, index: int) -> ServeObject:
        return self.serv_dict[self.speed_slist[index][2]]
