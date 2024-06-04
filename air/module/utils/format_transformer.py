from typing import Dict, Any
from ..serve.request import Request


class FormatTransformer:
    _str_to_int = {"Small": 1, "Medium": 2, "Large": 3}

    _int_to_str = {1: "Small", 2: "Medium", 3: "Large"}

    @staticmethod
    def speed(
            request: Request = None,
            message: Dict[str, Any] = None,
            speed: int | str = None,
    ) -> int | str:
        if request is not None:
            return FormatTransformer._str_to_int[request.target_speed]
        elif message is not None:
            return FormatTransformer._str_to_int[message["target_speed"]]
        elif isinstance(speed, int):
            return FormatTransformer._int_to_str[speed]
        elif isinstance(speed, str):
            return FormatTransformer._str_to_int[speed]
        else:
            raise RuntimeError("Invalid arguments")
