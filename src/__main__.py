#!/usr/bin/env python

from pathlib import Path
from sys import path as sys_path

if not __package__:
    # add the project root to the sys path
    file_path: Path = Path(__file__).resolve()
    root_path: str = file_path.parent.parent.as_posix()
    sys_path.insert(0, root_path)


if __name__ == "__main__":
    # setup logging configuration
    from src.utils.logger import setup_logger

    setup_logger()

    # run main app
    from src.app import main, update_config_key
    from src.services.msteams.teams import MsTeams, log_message
    from src.utils.constants import DEFAULT_ENV, ENV

    try:
        # check if the environment is valid
        if ENV not in ["dev", "prod"]:
            log_message(
                mode="warning",
                msg=f"invalid environment mode ⊱ {ENV} ⊰, using ⊱ {DEFAULT_ENV} ⊰ instead",
            )
            ENV = DEFAULT_ENV
            update_config_key(key="ENV", value=ENV)

        log_message(mode="info", msg=f"running on ⊱ {ENV} ⊰ mode")
        main()
    except Exception as e:  # noqa: BLE001
        log_message(mode="critical", msg=str(e))
        MsTeams.send_message(msg=str(e))
    except KeyboardInterrupt:
        log_message(mode="info", msg="app interrupted by the user")
