"""
Logging utility for the COCO_CODE CLI.
Provides formatted console output with color coding and progress indicators.
"""

from enum import Enum
from datetime import datetime


class LogLevel(Enum):
    """Log level types"""
    INFO = "[i]"
    SUCCESS = "[+]"
    WARNING = "[!]"
    ERROR = "[-]"
    HEADER = "[*]"
    STEP = "[>]"


class Logger:
    """Simple, elegant logging system for CLI output"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.start_time = datetime.now()

    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """Log a message with the specified level"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        display_icon = level.value
        print(f"[{timestamp}] {display_icon} {message}")

    def info(self, message: str):
        """Log an info message"""
        self.log(message, LogLevel.INFO)

    def success(self, message: str):
        """Log a success message"""
        self.log(message, LogLevel.SUCCESS)

    def warning(self, message: str):
        """Log a warning message"""
        self.log(message, LogLevel.WARNING)

    def error(self, message: str):
        """Log an error message"""
        self.log(message, LogLevel.ERROR)

    def header(self, message: str):
        """Log a header/section message"""
        print("\n" + "=" * 60)
        self.log(message, LogLevel.HEADER)
        print("=" * 60 + "\n")

    def step(self, message: str):
        """Log a step in the process"""
        self.log(message, LogLevel.STEP)

    def debug(self, message: str):
        """Log debug information (only if verbose)"""
        if self.verbose:
            self.log(f"[DEBUG] {message}", LogLevel.INFO)

    def progress(self, current: int, total: int, task: str = ""):
        """Show progress bar"""
        percentage = (current / total) * 100
        filled = int(20 * current // total)
        bar = "#" * filled + "-" * (20 - filled)
        print(f"\r[{bar}] {percentage:.0f}% {task}", end="", flush=True)
        if current == total:
            print()  # New line when complete

    def elapsed_time(self):
        """Display elapsed time since logger initialization"""
        elapsed = datetime.now() - self.start_time
        seconds = int(elapsed.total_seconds())
        minutes = seconds // 60
        seconds = seconds % 60
        if minutes > 0:
            self.success(f"Completed in {minutes}m {seconds}s")
        else:
            self.success(f"Completed in {seconds}s")

