from simple_websocket import Client
from typing import Dict, Any


class Request:

    def __init__(self, message: Dict[str, Any], ws: Client) -> None:
        self.type = None
        self.room_name = None
        self.target_speed = None
        self.ws = ws
        for key, value in message.items():
            setattr(self, key, value)
