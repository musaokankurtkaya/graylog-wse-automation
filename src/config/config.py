from json import JSONDecodeError
from json import load as json_load
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, set_key

from src.types import GraylogConfig, SMTPConfig, WindowsSecurityEvent

ROOT_FOLDER_PATH: Path = Path(__file__).parent.parent.parent

PROJECT_FOLDER_PATH: Path = ROOT_FOLDER_PATH / "src"

CONFIG_FOLDER_PATH: Path = PROJECT_FOLDER_PATH / "config"

ENV_FOLDER_PATH: Path = CONFIG_FOLDER_PATH / ".env"

DATA_FOLDER_PATH: Path = PROJECT_FOLDER_PATH / "data"


def load_config() -> dict[str, str | None]:
    """Reads the .env file and returns the settings as a dictionary.

    Returns
    -------
    dict[str, str | None]
        Configuration settings, if the .env file exists and is not empty. Otherwise, empty dictionary.
    """

    return dict(dotenv_values(dotenv_path=ENV_FOLDER_PATH))


def update_config_key(key: str, value: str) -> None:
    """Update the value of a key in the .env file.

    Parameters
    ----------
    key : str
        Key to set.
    value : str
        Value to set for the key.
    """

    set_key(
        dotenv_path=ENV_FOLDER_PATH,
        key_to_set=key,
        value_to_set=value,
        quote_mode="never",
    )


def load_graylog_conf(conf: dict[str, str | None]) -> GraylogConfig:
    """Load graylog configuration with the given config parameter.

    Parameters
    ----------
    conf : dict[str, str | None]
        The configuration settings as a dictionary from the .env file.

    Returns
    -------
    GraylogConfig
        Graylog configuration settings, if all the expected parameters are found. Otherwise, raises ValueError.

    Raises
    ------
    ValueError
        - If GRAYLOG_URL, GRAYLOG_USERNAME, GRAYLOG_PASSWORD, and GRAYLOG_SEARCH_QUERY_INTERVAL not found in .env file.
    """

    required_keys: list[str] = [
        "GRAYLOG_URL",
        "GRAYLOG_USERNAME",
        "GRAYLOG_PASSWORD",
        "GRAYLOG_SEARCH_QUERY_INTERVAL",
    ]
    for key in required_keys:
        if not conf.get(key):
            raise ValueError(f"{key} not set in .env file")

    graylog_conf: GraylogConfig = {
        k: v for k, v in conf.items() if k.startswith("GRAYLOG_")
    }  # pyright: ignore[reportAssignmentType]
    return graylog_conf


def load_smtp_conf(conf: dict[str, str | None]) -> SMTPConfig:
    """Load SMTP configuration with the given config parameter.

    Parameters
    ----------
    conf : dict[str, str | None]
        The configuration settings as a dictionary from the .env file.

    Returns
    -------
    SMTPConfig
        SMTP configuration settings, if all the expected parameters are found. Otherwise, raises ValueError.

    Raises
    ------
    ValueError
        - If SMTP_HOST, SMTP_PORT, SMTP_FROM_EMAIL, SMTP_FROM_EMAIL_APP_PASSWORD not found in .env file.
    """

    required_keys: list[str] = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_FROM_EMAIL",
        "SMTP_FROM_EMAIL_APP_PASSWORD",
        "SMTP_TO_EMAILS",
    ]
    for key in required_keys:
        if not conf.get(key):
            raise ValueError(f"{key} not set in .env file")

    smtp_conf: SMTPConfig = {k: v for k, v in conf.items() if k.startswith("SMTP_")}  # pyright: ignore[reportAssignmentType]
    return smtp_conf


def load_json_file(f_name: str) -> Any:
    """Load a JSON file from the data/ folder.

    Parameters
    ----------
    f_name : str
        The name of the file to load.

    Returns
    -------
    Any
        The parsed JSON content.

    Raises
    ------
    FileNotFoundError
        If the file is not found in data/ folder.
    ValueError
        If the file is empty.
    JSONDecodeError
        If the file is not a valid JSON file.
    """

    f_path: Path = DATA_FOLDER_PATH / f_name
    if not f_path.exists():
        raise FileNotFoundError(f"{f_name} not found in data/ folder")

    with open(file=f_path, encoding="utf-8") as f:
        try:
            f_content: list[WindowsSecurityEvent] = json_load(fp=f)
            if not f_content:
                raise ValueError(f"{f_name} not contains any data")
            return f_content
        except JSONDecodeError as e:
            raise JSONDecodeError(
                msg=f"{f_name} not a valid JSON file", doc=e.doc, pos=e.pos
            )
