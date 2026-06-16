from typing import Optional, Literal
from copy import copy
import logging
import sys
import click

TRACE_LOG_LEVEL = 5

class CustomFormatter(logging.Formatter):
    """
    A custom log formatter class that:

    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }
    icon_map = {
        5:  "⚪",
        10: "🔵",
        20: "🟢",
        30: "🟡",
        40: "🔴",
        50: "💀"
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: Optional[bool] = None,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)  # pragma: no cover

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self) -> bool:
        return sys.stderr.isatty()  # pragma: no cover

    def log_icon(self, levelno: int) -> str:
        return self.icon_map[levelno] + " "
    
    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        name = recordcopy.name
        asctime = recordcopy.asctime
        message = recordcopy.message
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            name = self.color_level_name(name, recordcopy.levelno)
            asctime = self.color_level_name(asctime, recordcopy.levelno)
            message = self.color_level_name(message, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["name"] = self.log_icon(recordcopy.levelno) + name + ":" + " " * (20 - len(recordcopy.name))
        recordcopy.__dict__["levelprefix"] = levelname + ":" + " " * (8 - len(recordcopy.levelname))
        recordcopy.__dict__["asctime"] = asctime + ":" + " " * (25 - len(recordcopy.asctime))
        recordcopy.__dict__["message"] = message
        return super().formatMessage(recordcopy)
