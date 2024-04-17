from flask import current_app, Blueprint
from flask_sock import Sock
from simple_websocket import Client
from queue import Queue
from json import loads
from .module import sched
from .module.serve.service_provider import ServiceProvider

bp = Blueprint("websocket", __name__, url_prefix="/websocket")
sock = Sock(current_app)

# schedule
queue = Queue()

service_provider = ServiceProvider()
scheduler = sched.Scheduler(queue, service_provider)
scheduler.daemon = True
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
        message["room_name"] = str(room_number)  # 房间号和房间名相同
        queue.put((message, ws))
