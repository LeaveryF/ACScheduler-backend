from threading import Thread, Timer, Lock
from queue import Queue

from ..utils.queue_object_factory import QueueObjectFactory
from ..serve.service_provider import ServiceProvider
from ..serve.request import Request
from ..utils.wait_queue import WaitQueue, WaitObject
from ..utils.serve_queue import ServeQueue, ServeObject
from ..utils.format_transformer import FormatTransformer
from ..serve.request_factory import RequestFactory


class Scheduler(Thread):

    def __init__(self, capacity: int = 10, daemon: bool = True):
        super().__init__(daemon=daemon)
        self.mutex = Lock()
        self.queue = Queue()
        self.serve_queue = ServeQueue(capacity)
        self.wait_queue = WaitQueue()
        self.service_provider = ServiceProvider(daemon=True)
        self.service_provider.start()

    def run(self):
        while True:
            with self.mutex:
                request = self.queue.get()

                # 1. 开关机请求
                if request.type == "SwitchPower":
                    self.handle_switch_power(request)
                    
                # 2. 调节请求
                elif request.type == "Adjust":
                    self.handle_adjust(request)
                    
                # 3. 温度达到请求
                elif request.type == "TemperatureReached":
                    self.handle_temperature_reached(request)
                    
                # 其它请求
                else:
                    self.service_provider.queue.put(request)

    # 功能：调度
    # 调用者：
    # handle_adjust()
    # 调用：
    # _enqueue_wait_object()
    # handle_cancel()
    # _evict()
    # _enqueue_serv_object()
    def schedule(self, request: Request):
        
        room_name = request.room_name
        target_wind_speed = FormatTransformer.speed(request)

        # 如果在等待队列中 先清除 重新调度 按调度规则调度
        if self.wait_queue.contains(room_name):
            self.wait_queue.pop(room_name=room_name)

        # * 如果在服务队列中 先清除 重新调度 调度等待时间最长的
        # 直接更新风速, 意味着只要被服务, 除非被抢占或达到目标, 否则可以随意改变风速
        if self.serve_queue.contains(room_name):
            self._update_serv_object(request=request)
            # self.serve_queue.pop(room_name=room_name)
            # self._enqueue_wait_object(request=request)
            # self.handle_cancel()
            return

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

    # 1. 开关机请求
    def handle_switch_power(self, request: Request):
        
        room_name = request.room_name
        
        # 如果是关机请求
        if request.is_ac_power_on == False:
            # 如果在等待队列中 清除
            if self.wait_queue.contains(room_name):
                self.wait_queue.pop(room_name=room_name)

            # 如果在服务队列中 清除 调度
            if self.serve_queue.contains(room_name):
                self.serve_queue.pop(room_name=room_name)
                self.handle_cancel()
        
        # 所有请求转发给 service_provider
        self.service_provider.queue.put(request)

    # 2. 调节请求
    def handle_adjust(self, request: Request):

        room_name = request.room_name
        target_wind_speed = FormatTransformer.speed(request)  # 获取目标风速

        # 在等待队列中
        if self.wait_queue.contains(room_name):
            old_wind_speed = self.wait_queue.get_wind_speed(room_name)

            # 风速不同, 进入调度
            if old_wind_speed != target_wind_speed:
                self.schedule(request)

            # 风速相同, 只是调整温度, 更新目标温度即可, 不用调度, 直接 serve

        # 在服务队列中
        elif self.serve_queue.contains(room_name):
            old_wind_speed = self.serve_queue.get_wind_speed(room_name)

            # 风速不同, 进入调度
            if old_wind_speed != target_wind_speed:
                self.schedule(request)

            # 风速相同, 只是调整温度, 更新目标温度即可

        # 不在队列中, 或者在队列中但是风速不同
        else:
            self.schedule()

        # 所有请求转发给 service_provider 因为目标风速应总是客户端的目标风速 即使还没被调度
        self.service_provider.queue.put(request)

    # 3. 温度达到请求
    def handle_temperature_reached(self, request: Request):
        
        room_name = request.room_name
        
        # 清除服务对象
        self.serve_queue.pop(room_name=room_name)
        self.handle_cancel()
        
        # 所有请求转发给 service_provider
        self.service_provider.queue.put(request)

    # 功能：处理等待对象s秒时间到达
    # 调用：
    # _evict()
    # _enqueue_serv_object()
    def handle_timeout(self):
        with self.mutex:
            wait_object = self.wait_queue.pop()

            # 如果服务队列中已经有了这个房间的服务对象, 那么进行更新
            # if self.serve_queue.contains(wait_object.room_name):
            #     self._update_serv_object(wait_object=wait_object)
            #     return

            # 服务队列未满, 直接为等待队列中的对象提供服务
            # elif not self.serve_queue.full():
            #     self._enqueue_serv_object(wait_object=wait_object)
            #     return

            # 尝试将优先级最低的服务对象踢出
            # elif self.serve_queue[0].speed < wait_object.speed:
            #     # 优先级更高, 抢占服务对象
            #     self._evict(oldest=False)

            # 将最长服务对象踢出(最早对象)
            # else:
            self._evict(oldest=True)

            # 进入服务队列
            self._enqueue_serv_object(wait_object=wait_object)

    # 功能：处理中途需要调度的情况 删除最早的等待对象 提供服务
    # 调用者：
    # handle_switch_power()
    # handle_temperature_reached()
    # 前置条件：服务队列一定未满
    # 后置条件：
    # wait_queue 删除最早的等待对象
    # _enqueue_serv_object()
    def handle_cancel(self):

        # 找到等待时长最大的 即最早的等待对象 进行调度 进入服务队列
        wait_object = self.wait_queue.pop(oldest=True)  # todo
        self._enqueue_serv_object(wait_object=wait_object)

    # 功能：发送关机请求 (dummy request)
    # 调用者：
    # _evict()
    # 后置条件：
    # service_provider 获得 DummyPowerOff 请求
    def _cancel_service(self, serve_object: ServeObject):
        dummy_poweroff_request = RequestFactory.create_request(
            serve_object=serve_object
        )
        self.service_provider.queue.put(dummy_poweroff_request)

    # 功能：构造等待对象 加入等待队列
    # 调用者：
    # schedule()
    # _evict()
    # 后置条件：
    # wait_queue 新增等待对象
    def _enqueue_wait_object(self, serve_object: ServeObject = None, request: Request = None):
        wait_object = None
        if serve_object is not None:
            wait_object = QueueObjectFactory.create_wait_object(
                serve_object=serve_object
            )
        elif request is not None:
            wait_object = QueueObjectFactory.create_wait_object(request=request)
        wait_object.timer = Timer(120, self.handle_timeout)
        self.wait_queue.add(wait_object)

    # 功能：构造服务对象 加入服务队列
    # 调用者：
    # schedule()
    # handle_timeout()
    # handle_cancel()
    # 后置条件：
    # serve_queue 新增服务对象
    # service_provider 获得 Serve 请求
    def _enqueue_serv_object(self, request: Request = None, wait_object: WaitObject = None):
        if request is not None:
            serve_object = QueueObjectFactory.create_serve_object(request=request)
            request = RequestFactory.create_request(request=request)
        elif wait_object is not None:
            serve_object = QueueObjectFactory.create_serve_object(wait_object=wait_object)
            request = RequestFactory.create_request(wait_object=wait_object)
        self.serve_queue.add(serve_object)
        self.service_provider.queue.put(request)

    # * called by "handle_timeout" 更新服务队列中的服务对象
    # 功能：请求正在被服务 风速不等时 更新服务队列中的服务对象 的风速
    # 调用者：
    # handle_adjust()
    # 后置条件：
    # serve_queue 被更新
    # service_provider 获得 Serve 请求
    def _update_serv_object(self, wait_object: WaitObject = None, request: Request = None):
        # if wait_object is not None:
        #     request = RequestFactory.create_request(wait_object=wait_object)
        #     serve_object = QueueObjectFactory.create_serve_object(wait_object=wait_object)
        #     self.serve_queue.update(serve_object)
        #     self.service_provider.queue.put(request)
        if request is not None:
            serve_object = QueueObjectFactory.create_serve_object(request=request)
            self.serve_queue.update(serve_object)
            request = RequestFactory.create_request(request=request)
            self.service_provider.queue.put(request)

    # 功能：抢占服务对象
    # 调用者：
    # schedule()
    # handle_timeout()
    # 后置条件：
    # serve_queue 删除最早的服务对象
    # _cancel_service()
    # _enqueue_wait_object()
    def _evict(self, oldest: bool = False):
        popped_serve_object = self.serve_queue.pop(oldest)
        # 1. 发送关机请求 (dummy request)
        self._cancel_service(serve_object=popped_serve_object)
        # 2. 旧的服务对象进入等待队列
        self._enqueue_wait_object(serve_object=popped_serve_object)
