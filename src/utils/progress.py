import math
import shutil
from time import perf_counter

MAX_INCREMENT_TIME_LOGS = 32


class Progress:
    def __init__(self, total: int):
        self.current = 0
        self.total = total
        self.__increment_time_logs = []

    def increment(self):
        self.current += 1
        if len(self.__increment_time_logs) >= MAX_INCREMENT_TIME_LOGS:
            self.__increment_time_logs.pop(0)
        self.__increment_time_logs.append(perf_counter())

    @property
    def eta(self) -> float:
        if len(self.__increment_time_logs) <= 1:
            return float("inf")

        time_between = 0
        for idx in range(1, len(self.__increment_time_logs)):
            prev_time = self.__increment_time_logs[idx - 1]
            curr_time = self.__increment_time_logs[idx]
            time_between += curr_time - prev_time
        time_between /= len(self.__increment_time_logs)
        speed = 1 / time_between

        return (self.total - self.current) / speed

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 1.0
        else:
            return self.current / self.total

    def bar_str(self, width: int) -> str:
        inner_width = width - 2
        filled_width = math.floor(inner_width * self.percent)
        empty_width = inner_width - filled_width
        return f"[{"=" * filled_width}{" " * empty_width}]"
    
    def percent_str(self) -> str:
        return f"[{self.percent * 100:.0f}%]"
    
    def eta_str(self) -> str:
        eta = self.eta
        unit = "sec"

        if eta >= 60 * 60 * 24 * 365:
            return "[ETA: never]"
        elif eta >= 60 * 60 * 24 * 30:
            eta /= 60 * 60 * 24 * 30
            unit = "months"
        elif eta >= 60 * 60 * 24 * 7:
            eta /= 60 * 60 * 24 * 7
            unit = "weeks"
        elif eta >= 60 * 60 * 24:
            eta /= 60 * 60 * 24
            unit = "days"
        elif eta >= 60 * 60:
            eta /= 60 * 60
            unit = "hours"
        elif eta >= 60:
            eta /= 60
            unit = "min"

        return f"[ETA: {eta:.1f} {unit}]"
    
    def __repr__(self) -> str:
        console_width = shutil.get_terminal_size((12, 24)).columns
        
        percent = self.percent_str()
        eta = self.eta_str()

        bar_max_width = 30
        bar_width = min(bar_max_width, console_width - 2 - len(percent) - len(eta))
        bar = self.bar_str(bar_width)

        text = f"{bar} {percent} {eta}"
        padding = " " * (console_width - len(text))
        
        return text + padding
