from datetime import datetime

from .format_transformer import FormatTransformer
from .serve_queue import ServeObject
from .wait_queue import WaitObject
from ..serve.request import Request


class QueueObjectFactory:
    service_id_counter = 0

    @staticmethod
    def create_serve_object(request: Request = None, wait_object: WaitObject = None) -> ServeObject:
        """
        生成服务对象
        """
        if request is not None:
            speed = FormatTransformer.speed(speed=request.target_speed)
            start_time = datetime.now()
            QueueObjectFactory.service_id_counter += 1
            service_id = QueueObjectFactory.service_id_counter
            room_name = request.room_name
            ws = request.ws
            return ServeObject(speed, start_time, service_id, room_name, ws)
        elif wait_object is not None:
            speed = wait_object.speed
            start_time = datetime.now()
            QueueObjectFactory.service_id_counter += 1
            service_id = QueueObjectFactory.service_id_counter
            room_name = wait_object.room_name
            ws = wait_object.ws
            return ServeObject(speed, start_time, service_id, room_name, ws)
        else:
            raise RuntimeError("Unimplemented")

    @staticmethod
    def create_wait_object(request: Request = None, serve_object: ServeObject = None) -> WaitObject:
        """
        生成等待服务对象
        """
        if request is not None:
            speed = FormatTransformer.speed(speed=request.target_speed)
            room_name = request.room_name
            ws = request.ws
            return WaitObject(speed, room_name, ws)
        elif serve_object is not None:
            speed = serve_object.speed
            room_name = serve_object.room_name
            ws = serve_object.ws
            return WaitObject(speed, room_name, ws)
        else:
            raise RuntimeError("Unimplemented")