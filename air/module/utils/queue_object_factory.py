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
            room_number = request.room_number
            ws = request.ws
            temp = request.target_temp
            mode = request.target_mode
            return ServeObject(speed, start_time, service_id, room_number, ws, temp, mode)
        elif wait_object is not None:
            speed = wait_object.speed
            start_time = datetime.now()
            QueueObjectFactory.service_id_counter += 1
            service_id = QueueObjectFactory.service_id_counter
            room_number = wait_object.room_number
            ws = wait_object.ws
            temp = wait_object.temp
            mode = wait_object.mode
            return ServeObject(speed, start_time, service_id, room_number, ws, temp, mode)
        else:
            raise RuntimeError("Unimplemented")

    @staticmethod
    def create_wait_object(request: Request = None, serve_object: ServeObject = None) -> WaitObject:
        """
        生成等待服务对象
        """
        if request is not None:
            speed = FormatTransformer.speed(speed=request.target_speed)
            room_number = request.room_number
            ws = request.ws
            start_time = datetime.now()
            temp = request.target_temp
            mode = request.target_mode
            return WaitObject(speed, room_number, ws, start_time, temp, mode)
        elif serve_object is not None:
            speed = serve_object.speed
            room_number = serve_object.room_number
            ws = serve_object.ws
            start_time = datetime.now()
            temp = serve_object.temp
            mode = serve_object.mode
            return WaitObject(speed, room_number, ws, start_time, temp, mode)
        else:
            raise RuntimeError("Unimplemented")
