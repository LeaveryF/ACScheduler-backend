from typing import Dict, Any

from simple_websocket import Client

from ..serve.request import Request
from ..utils.format_transformer import FormatTransformer
from ..utils.serve_queue import ServeObject
from ..utils.wait_queue import WaitObject


class RequestFactory:

    @staticmethod
    def create_request(
            message: Dict[str, Any] = None,
            ws: Client = None,
            serve_object: ServeObject = None,
            wait_object: WaitObject = None,
            request: Request = None,
    ) -> Request:
        if message is not None and ws is not None:
            return Request(message, ws)

        elif serve_object is not None:
            # 根据服务对象生成关机请求 (dummy)
            dummy_message = {
                "type": "DummyPowerOff",
                "is_ac_power_on": False,
                "room_number": serve_object.room_number,
            }
            ws = serve_object.ws
            return Request(dummy_message, ws)

        elif wait_object is not None:
            dummy_message = {
                "type": "Serve",  # update: "Serve" type 区分于 "Adjust"
                "target_mode": wait_object.mode,
                "target_temp": wait_object.temp,
                "target_speed": FormatTransformer.speed(speed=wait_object.speed),
                "room_number": wait_object.room_number,
            }
            ws = wait_object.ws
            return Request(dummy_message, ws)

        elif request is not None:
            request.type = "Serve"
            return request

        else:
            raise RuntimeError("Unimplemented")
