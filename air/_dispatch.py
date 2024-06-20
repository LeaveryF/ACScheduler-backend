from flask import current_app, Blueprint
from flask_sock import Sock
from simple_websocket import Client
from json import loads
from .module.sched.scheduler import Scheduler
from .module.serve.request_factory import RequestFactory

bp = Blueprint("websocket", __name__, url_prefix="/websocket")
sock = Sock(current_app)

scheduler = Scheduler(daemon=True)
scheduler.start()


@sock.route('/<int:room_number>', bp=bp)
def dispatch(ws: Client, room_number: int):
    """将房间发出的消息发配给调度器

    Args:
        ws (simple_websocket.Client): websocket连接客户端
        room_number (int): 发出信号的房间号
    """
    while True:
        message = ws.receive()
        message = loads(message)
        message["room_number"] = str(room_number)  # 房间号和房间名相同
        request = RequestFactory.create_request(message=message, ws=ws)
        scheduler.queue.put(request)
