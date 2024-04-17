from simple_websocket import Client
from datetime import datetime
from typing import Tuple, Dict, Any


class ServiceProvider:

    def __init__(self):
        pass

    def serve(self, service: Tuple[int, datetime, int, str, Client]):
        # TODO: implement this
        pass

    def serve_switch_power(self, message: Dict[str, Any], ws: Client):
        pass

    def serv_update_cost(self, message: Dict[str, Any], ws: Client):
        pass

    def serv_temperature(self, message: Dict[str, Any], ws: Client):
        pass
