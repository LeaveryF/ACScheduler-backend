_str_to_int = {
    "Small": 1,
    "Medium": 2,
    "Large": 3
}

_int_to_str = {
    1: "Small",
    2: "Medium",
    3: "Large"
}


class WindSpeedMapper:

    @staticmethod
    def str_to_int(wind_speed: str) -> int:
        return _str_to_int[wind_speed]

    @staticmethod
    def int_to_str(wind_speed: int) -> str:
        return _int_to_str[wind_speed]
