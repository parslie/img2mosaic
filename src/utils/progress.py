import math
import shutil


class Progress:
    def __init__(self, total: int):
        self.current = 0
        self.total = total
        self.speed = 0

    def bar_str(self, width: int) -> str:
        inner_width = width - 2
        filled_width = math.floor(inner_width * self.current / self.total)
        empty_width = inner_width - filled_width
        return f"[{"=" * filled_width}{" " * empty_width}]"
    
    def percent_str(self) -> str:
        return f"[{self.current / self.total * 100:.0f}%]"
    
    def eta_str(self) -> str:
        if self.speed == 0:
            return f"[ETA: N/A]"
        
        eta = (self.total - self.current) / self.speed
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
