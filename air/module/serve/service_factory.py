from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

from simple_websocket import Client
from ..utils.wind_speed_mapper import WindSpeedMapper


class ServiceFactory:

    @staticmethod
    def create_service(message: Dict[str, Any], ws: Client) -> Tuple[int, datetime, int, str, Client]:
        """
        生成服务对象
        :param message: 客户端发送的 json 格式报文
        :param ws: 连接客户端的 websocket
        :return: (风速, 服务开始时间戳, 服务对象ID, 房间号, WebSocket)
        """
        now = datetime.now()
        wind_speed = WindSpeedMapper.str_to_int(message["target_speed"])
        service_id = message["service_id"]
        room_name = message["room_name"]
        return wind_speed, now, service_id, room_name, ws

    @staticmethod
    def create_wait_object(message: Dict[str, Any], ws: Client) -> Tuple[datetime, int, str, Client]:
        """
        生成等待服务对象
        :param message: 客户端发送的 json 格式报文
        :param ws: 连接客户端的 websocket
        :return: (结束等待时间戳, 风速, 房间号, WebSocket)
        """
        now = datetime.now()
        end_time = now + timedelta(minutes=2)
        wind_speed = WindSpeedMapper.str_to_int(message["target_speed"])
        room_name = message["room_name"]

        return end_time, wind_speed, room_name, ws

    @staticmethod
    def create_service_by_wait_object(
            wait_service: Tuple[datetime, int, str, Client],
            service_id: int
    ) -> Tuple[int, datetime, int, str, Client]:
        _, wind_speed, room_name, ws = wait_service
        now = datetime.now()
        return wind_speed, now, service_id, room_name, ws
    
    @staticmethod
    def create_wait_object_by_service(
            service: Tuple[int, datetime, int, str, Client]
    ) -> Tuple[datetime, int, str, Client]:
        now = datetime.now()
        end_time = now + timedelta(minutes=2)
        wind_speed, _, _, room_name, ws = service
        return end_time, wind_speed, room_name, ws
