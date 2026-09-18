import logging
from datetime import UTC, datetime
from os import makedirs as os_makedirs
from os import path as os_path
from typing import ClassVar

from pythonjsonlogger.json import JsonFormatter

from .constants import ENV, IS_PROD, LOG_FOLDER_PATH


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to the console log messages.

    Attributes
    ----------
    ANSI_COLORS : dict[str, str]
        ANSI colors for the log messages.
    LOG_COLORS : dict[str, str]
        Log level colors for the log messages.
    """

    ANSI_COLORS: ClassVar[dict[str, str]] = {
        "red": "\033[1;31;40m",
        "green": "\033[1;32;40m",
        "yellow": "\033[1;33;40m",
        "purple": "\033[1;35;40m",
        "cyan": "\033[1;36;40m",
        "reset": "\033[0m",
    }

    LOG_COLORS: ClassVar[dict[str, str]] = {
        "notset": "reset",
        "debug": "cyan",
        "info": "green",
        "warning": "yellow",
        "error": "red",
        "critical": "purple",
    }

    def __init__(self, fmt: str) -> None:
        super().__init__(fmt=fmt)

    def format(self, record: logging.LogRecord) -> str:
        log_level: str = record.levelname.lower()
        log_color: str = self.LOG_COLORS.get(log_level, "reset")

        orig_levelname: str = record.levelname

        record.levelname = f"{self.ANSI_COLORS[log_color]}[{log_level}:{record.name}]{self.ANSI_COLORS['reset']}"

        formatted: str = super().format(record=record)

        record.levelname = orig_levelname

        return formatted


def setup_console_handler(level: int = logging.DEBUG) -> logging.Handler:
    """Create and return the console handler for colored log output."""

    console_handler = logging.StreamHandler()

    fmt: str = "%(levelname)s %(message)s"
    console_handler.setFormatter(fmt=ColoredFormatter(fmt=fmt))

    console_handler.setLevel(level=level)

    return console_handler


def setup_file_handler(level: int = logging.WARNING) -> logging.Handler:
    """Create and return the file handler for JSON formatted logs."""

    # create log folder if it doesn't exist
    now: datetime = datetime.now(tz=UTC)
    log_folder_path: str = os_path.join(LOG_FOLDER_PATH, str(now.year))
    os_makedirs(log_folder_path, exist_ok=True)

    # create log file path based on the current month
    log_file_name: str = f"log_{now.month:02d}.log"
    log_file_path: str = os_path.join(log_folder_path, log_file_name)

    file_handler = logging.FileHandler(filename=log_file_path, encoding="utf-8")

    file_formatter = logging.Formatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    json_file_formatter = JsonFormatter(
        fmt=file_formatter._fmt,
        datefmt=file_formatter.datefmt,
        json_ensure_ascii=False,
        rename_fields={"levelname": "level", "asctime": "timestamp"},
        static_fields={"environment": ENV},
    )

    file_handler.setFormatter(fmt=json_file_formatter)

    file_handler.setLevel(level=level)

    return file_handler


def setup_logger(name: str | None = None) -> logging.Logger:
    """Setup logger for the app.

    Parameters
    ----------
    name : str, optional
        Logger name, by default None.

    - Log level: **DEBUG** for (console), **WARNING** for (file)
    - Log format: **'%(levelname)s %(name)s %(message)s'** (console), **formatted with JSON** (file)
    - Log date format: **'%Y-%m-%d %H:%M:%S'**
    - Log file name: **log_01.log**, **log_02.log**, ...
    - Log file path: **/path/to/logs/{year}/log_{month}.log**
    """

    logger: logging.Logger = logging.getLogger(name=name)

    logger.setLevel(level=logging.DEBUG)

    # add console and file handlers based on the environment
    if IS_PROD:
        logger.addHandler(hdlr=setup_file_handler(level=logging.WARNING))

    logger.addHandler(hdlr=setup_console_handler(level=logging.DEBUG))

    return logger


def log_message(mode: str, msg: str, **log_kwargs) -> None:
    """Log a message with the given mode & message.

    Parameters
    ----------
    mode : str
        Log level mode (notset, debug, info, warning, error, critical)
    msg : str
        Log message to log.
    **log_kwargs
        Additional log keyword arguments to pass to the logger (e.g. extra, stack_info, exc_info etc.)
    """

    levels: dict[str, int] = {
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    level: int = levels.get(mode, logging.INFO)
    logging.log(level=level, msg=msg, **log_kwargs)  # noqa: LOG015
