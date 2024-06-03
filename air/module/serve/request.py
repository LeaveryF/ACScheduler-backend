from simple_websocket import Client
from typing import Dict, Any
from ..utils.serve_queue import ServeObject
from ..utils.wait_queue import WaitObject
from ..utils.format_transformer import FormatTransformer


class Request:

    def __init__(self, message: Dict[str, Any], ws: Client) -> None:
        self.type = None
        self.room_name = None
        self.target_speed = None
        self.ws = ws
        for key, value in message.items():
            setattr(self, key, value)


class RequestFactory:

    @staticmethod
    def create_request(
            message: Dict[str, Any] = None,
            ws: Client = None,
            serve_object: ServeObject = None,
            wait_object: WaitObject = None,
    ) -> Request:
        if message is not None and ws is not None:
            return Request(message, ws)

        elif serve_object is not None:
            # 根据服务对象生成关机请求 (dummy)
            dummy_message = {
                "type": "SwitchPower",
                "is_ac_power_on": False,
                "room_name": serve_object.room_name,
            }
            ws = serve_object.ws
            return Request(dummy_message, ws)

        elif wait_object is not None:
            dummy_message = {
                "type": "Adjust",
                "target_mode": "Cold",  # TODO: 目标模式需要记录吗？
                "target_temp": 22,  # TODO: 目标温度需要记录吗？
                "target_speed": FormatTransformer.speed(speed=wait_object.speed),
            }
            ws = wait_object.ws
            return Request(dummy_message, ws)

        else:
            raise RuntimeError("Unimplemented")
