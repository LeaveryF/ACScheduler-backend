import threading
from queue import Queue
from ..utils.queue_object_factory import QueueObjectFactory
from ..serve.service_provider import ServiceProvider
from ..serve.request import Request
from ..utils.wait_queue import WaitQueue, WaitObject
from ..utils.serve_queue import ServeQueue, ServeObject
from ..utils.format_transformer import FormatTransformer
from ..serve.request_factory import RequestFactory


class Scheduler(threading.Thread):

    def __init__(self, capacity: int = 10, daemon: bool = True):
        super().__init__(daemon=daemon)
        self.sema = threading.Semaphore(0)
        self.mutex = threading.Lock()
        self.queue = Queue()
        self.serve_queue = ServeQueue(capacity)
        self.wait_queue = WaitQueue()
        self.service_provider = ServiceProvider(daemon=True)
        self.service_provider.start()

    def run(self):
        while True:
            self.sema.acquire()

            with self.mutex:
                request = self.queue.get()

                if request.type == "Adjust":
                    self.handle_adjust(request)
                else:
                    self.service_provider.queue.put(request)
                    self.service_provider.sema.release()

    def schedule(self, request: Request):

        target_wind_speed = FormatTransformer.speed(request)

        # 如果服务队列已满, 进行优先级调度
        if self.serve_queue.full():

            # 如果服务队列中风速最小的都比请求的要大, 那么请求进入等待队列
            if self.serve_queue[0].speed >= target_wind_speed:
                self._enqueue_wait_object(request=request)
                return

            # 优先级更高, 抢占服务对象
            self._evict()

        # 进入服务队列
        self._enqueue_serv_object(request=request)

    def handle_adjust(self, request: Request):

        room_number = request.room_number
        target_wind_speed = FormatTransformer.speed(request)  # 获取目标风速

        # 在等待队列中
        if self.wait_queue.contains(room_number):
            old_wind_speed = self.wait_queue.get_wind_speed(room_number)

            # 风速相同, 不用调度, 直接 serve
            if old_wind_speed == target_wind_speed:
                self.service_provider.queue.put(request)
                self.service_provider.sema.release()
                return

            # 风速不同, 更新等待队列中的风速
            self.wait_queue.update_wind_speed(room_number, target_wind_speed)
            return

        # 在服务队列中
        if self.serve_queue.contains(room_number):
            old_wind_speed = self.serve_queue.get_wind_speed(room_number)

            # 风速相同, 只是调整温度, 更新目标温度即可
            if old_wind_speed == target_wind_speed:
                self.service_provider.queue.put(request)
                self.service_provider.sema.release()
                return

            # 风速不同, 进入调度

        # 不在队列中, 或者在服务队列中但是风速不同
        self.schedule(request)

    def handle_timeout(self):
        with self.mutex:
            wait_object = self.wait_queue.pop()

            # 如果服务队列中已经有了这个房间的服务对象, 那么进行更新
            if self.serve_queue.contains(wait_object.room_number):
                self._update_serv_object(wait_object=wait_object)
                return

            # 服务队列未满, 直接为等待队列中的对象提供服务
            elif not self.serve_queue.full():
                self._enqueue_serv_object(wait_object=wait_object)
                return

            # 尝试将优先级最低的服务对象踢出
            elif self.serve_queue[0].speed < wait_object.speed:
                # 优先级更高, 抢占服务对象
                self._evict(oldest=False)

            # 将最长服务对象踢出(最早对象)
            else:
                self._evict(oldest=True)

            # 进入服务队列
            self._enqueue_serv_object(wait_object=wait_object)

    def _cancel_service(self, serve_object: ServeObject):
        dummy_poweroff_request = RequestFactory.create_request(
            serve_object=serve_object
        )
        self.service_provider.queue.put(dummy_poweroff_request)
        self.service_provider.sema.release()

    def _enqueue_wait_object(self, serve_object: ServeObject = None, request: Request = None):
        wait_object = None
        if serve_object is not None:
            wait_object = QueueObjectFactory.create_wait_object(
                serve_object=serve_object
            )
        elif request is not None:
            wait_object = QueueObjectFactory.create_wait_object(request=request)
        self.wait_queue.add(wait_object)
        timer = threading.Timer(120, self.handle_timeout)
        timer.start()

    def _enqueue_serv_object(self, request: Request = None, wait_object: WaitObject = None):
        if request is not None:
            serve_object = QueueObjectFactory.create_serve_object(request=request)
            self.serve_queue.add(serve_object)
            self.service_provider.queue.put(request)
            self.service_provider.sema.release()
        elif wait_object is not None:
            serve_object = QueueObjectFactory.create_serve_object(wait_object=wait_object)
            self.serve_queue.add(serve_object)
            self.service_provider.queue.put(request)
            self.service_provider.sema.release()

    def _update_serv_object(self, wait_object: WaitObject = None):
        if wait_object is not None:
            request = RequestFactory.create_request(wait_object=wait_object)
            serve_object = QueueObjectFactory.create_serve_object(wait_object=wait_object)
            self.serve_queue.update(serve_object)
            self.service_provider.queue.put(request)
            self.service_provider.sema.release()

    def _evict(self, oldest: bool = False):
        popped_serve_object = self.serve_queue.pop(oldest)
        # 1. 发送关机请求 (dummy request)
        self._cancel_service(serve_object=popped_serve_object)
        # 2. 旧的服务对象进入等待队列
        self._enqueue_wait_object(serve_object=popped_serve_object)
